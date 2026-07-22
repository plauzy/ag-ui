"""Agentic Chat feature — a baseline CAO run.

A single mock_cli worker turn projected through the run plane:
``RUN_STARTED -> STATE_SNAPSHOT -> STEP_STARTED -> (message dispatch) ->
STEP_FINISHED -> RUN_FINISHED(success)``. Keyless and deterministic.
"""

from __future__ import annotations

from fastapi import FastAPI, Request

from ._common import fleet_snapshot, make_bus, rec, run_response

_SESSION = "cao-agentic-chat"

_RECORDS = [
    rec(
        "launch",
        terminal_id="t-worker",
        session_name=_SESSION,
        detail={
            "agent_name": "assistant",
            "provider": "mock_cli",
            "event_type": "post_create_terminal",
        },
    ),
    rec(
        "handoff",
        terminal_id="t-worker",
        session_name=_SESSION,
        detail={
            "sender": "t-worker",
            "receiver": "user",
            "orchestration_type": "send_message",
            "event_type": "post_send_message",
        },
    ),
    rec(
        "completion",
        terminal_id="t-worker",
        session_name=_SESSION,
        detail={"agent_name": "assistant", "event_type": "post_kill_terminal"},
    ),
]

app = FastAPI(title="CAO — agentic_chat")


@app.post("/")
async def run(request: Request):
    return await run_response(
        request,
        snapshot_fn=fleet_snapshot,
        bus_subscribe_fn=make_bus(_RECORDS),
    )
