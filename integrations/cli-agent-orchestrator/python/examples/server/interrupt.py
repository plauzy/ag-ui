"""Interrupt feature — the flagship differentiator.

A mock_cli worker hits a permission prompt; CAO's ``AgentHandoffWithApproval``
construct opens an ``Interrupt``, and the run plane closes the run with
``RUN_FINISHED outcome={type:"interrupt", interrupts:[…]}``. The client answers
by re-running with ``resume:[{ interruptId, payload:{approved: true|false} }]``,
which CAO resolves idempotently (exactly-once) against the waiting process.

This is the round-trip no API-wrapper integration can demonstrate: approving or
denying a *live* CLI permission prompt from the browser through AG-UI's standard
interrupt lifecycle. Keyless — a no-op delivery stands in for the real tmux
paste so the demo needs no processes or keys, while exercising CAO's real
interrupt registry and run-plane code path.
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, Request

from cli_agent_orchestrator.services.agui.base import RecordingUiEmitter
from cli_agent_orchestrator.services.agui.handoff_approval import (
    AgentHandoffWithApproval,
)

from ._common import fleet_snapshot, run_response

_SESSION = "cao-interrupt"


class _NoopDelivery:
    """Keyless stand-in for tmux answer delivery (real path is thread-safe I/O).

    Returning cleanly lets ``AgentHandoffWithApproval.resume`` commit the
    decision exactly as it would after a real paste — so the interrupt registry,
    idempotency, and run-plane resolution are all genuinely exercised without a
    live process.
    """

    def send_input(self, terminal_id: str, text: str, **kwargs: Any) -> None:
        return None

    def send_special_key(self, terminal_id: str, key: str) -> bool:
        return True


# Module-level construct: one shared approval registry for the demo server.
_construct = AgentHandoffWithApproval(RecordingUiEmitter(), answer_delivery=_NoopDelivery())
# thread_id -> interrupt_id, so a fresh "start" per thread shows a prompt and a
# resume answers that thread's own interrupt.
_thread_interrupt: Dict[str, str] = {}

app = FastAPI(title="CAO — interrupt")


def _ensure_pending(thread_id: str) -> None:
    """Open an interrupt for this thread if none is currently pending."""
    existing_id = _thread_interrupt.get(thread_id)
    existing = _construct.get_interrupt(existing_id) if existing_id else None
    if existing is not None and not existing.resolved:
        return
    interrupt = _construct.on_provider_waiting(
        terminal_id=f"{thread_id}:mock",
        provider="mock_cli",
        raw_prompt="Allow mock_cli to run `rm -rf build/`? [y/n]",
        session_name=_SESSION,
    )
    _thread_interrupt[thread_id] = interrupt.id


@app.post("/")
async def run(request: Request):
    body = await request.json()  # cached by Starlette; run_response re-reads it
    thread_id = str(body.get("threadId") or body.get("thread_id") or "default")
    resume = body.get("resume") or []
    if not resume:
        # A run with no answer starts (or re-shows) the permission prompt so the
        # run plane emits the interrupt outcome.
        _ensure_pending(thread_id)
    return await run_response(
        request,
        approval_construct=_construct,
        snapshot_fn=fleet_snapshot,
    )
