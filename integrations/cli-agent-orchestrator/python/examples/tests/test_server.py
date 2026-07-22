"""Keyless protocol-contract tests for the CAO AG-UI example server.

These assert the *wire contract* CAO's run plane produces for each Dojo feature
— fail-closed, secret-free, and independent of the LLM-driven Dojo frontend. A
broken run-plane contract (or a regression in the fixtures) turns these red.

Run:  uv run --extra test pytest        (or: pytest)
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from server import app

client = TestClient(app)


def _run_input(thread_id: str, **extra: Any) -> Dict[str, Any]:
    body = {
        "threadId": thread_id,
        "runId": f"run-{thread_id}",
        "state": {},
        "messages": [],
        "tools": [],
        "context": [],
        "forwardedProps": {},
    }
    body.update(extra)
    return body


def _frames(path: str, body: Dict[str, Any]) -> List[Dict[str, Any]]:
    """POST a RunAgentInput and decode the data:-only SSE frames to dicts."""
    resp = client.post(path, json=body)
    assert resp.status_code == 200, (resp.status_code, resp.text)
    frames: List[Dict[str, Any]] = []
    for line in resp.text.splitlines():
        if line.startswith("data: "):
            frames.append(json.loads(line[len("data: ") :]))
    return frames


def _types(frames: List[Dict[str, Any]]) -> List[str]:
    return [f.get("type") for f in frames]


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200 and resp.json()["status"] == "ok"


def test_agentic_chat_lifecycle():
    frames = _frames("/agentic-chat/", _run_input("chat"))
    types = _types(frames)
    assert types[0] == "RUN_STARTED"
    assert types[-1] == "RUN_FINISHED"
    # A worker step is projected between start and finish.
    assert "STEP_STARTED" in types and "STEP_FINISHED" in types
    # Success outcome (no interrupt).
    assert frames[-1].get("outcome", {}).get("type") == "success"


def test_shared_state_snapshot_and_delta():
    frames = _frames("/shared-state/", _run_input("state"))
    types = _types(frames)
    assert "STATE_SNAPSHOT" in types
    assert "STATE_DELTA" in types
    # The delta is an RFC-6902 patch touching /last_file_mod.
    delta = next(f for f in frames if f.get("type") == "STATE_DELTA")
    paths = [op.get("path") for op in delta.get("delta", [])]
    assert "/last_file_mod" in paths


def test_human_in_the_loop_emits_approval_card():
    frames = _frames("/human-in-the-loop/", _run_input("hitl"))
    customs = [f for f in frames if f.get("type") == "CUSTOM"]
    gen_ui = [f for f in customs if f.get("name") == "cao.generative_ui"]
    assert gen_ui, _types(frames)
    assert gen_ui[0]["value"].get("component") == "approval_card"


def test_interrupt_outcome_then_approve_resume():
    # 1) A fresh run surfaces the interrupt outcome.
    frames = _frames("/interrupt/", _run_input("intr-approve"))
    assert frames[-1]["type"] == "RUN_FINISHED"
    outcome = frames[-1]["outcome"]
    assert outcome["type"] == "interrupt"
    interrupts = outcome["interrupts"]
    assert interrupts, "expected at least one open interrupt"
    interrupt_id = interrupts[0]["id"]

    # 2) Answering with approved:true resolves it -> success.
    resume_frames = _frames(
        "/interrupt/",
        _run_input(
            "intr-approve",
            resume=[
                {
                    "interruptId": interrupt_id,
                    "status": "resolved",
                    "payload": {"approved": True},
                }
            ],
        ),
    )
    assert resume_frames[-1]["type"] == "RUN_FINISHED"
    assert resume_frames[-1]["outcome"]["type"] == "success"


def test_interrupt_deny_resume():
    frames = _frames("/interrupt/", _run_input("intr-deny"))
    outcome = frames[-1]["outcome"]
    assert outcome["type"] == "interrupt"
    interrupt_id = outcome["interrupts"][0]["id"]

    resume_frames = _frames(
        "/interrupt/",
        _run_input(
            "intr-deny",
            # status="cancelled" maps to a deny decision in the run plane.
            resume=[{"interruptId": interrupt_id, "status": "cancelled"}],
        ),
    )
    assert resume_frames[-1]["outcome"]["type"] == "success"


def test_privacy_boundary_no_prompt_body_on_wire():
    # The raw permission prompt body must never reach the wire (metadata only).
    frames = _frames("/interrupt/", _run_input("intr-privacy"))
    blob = json.dumps(frames)
    assert "rm -rf" not in blob
    # The interrupt still carries its classified reason + metadata.
    outcome = frames[-1]["outcome"]
    interrupt = outcome["interrupts"][0]
    assert interrupt.get("reason")
    assert interrupt.get("metadata", {}).get("provider") == "mock_cli"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
