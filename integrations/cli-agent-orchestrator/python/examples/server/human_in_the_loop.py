"""Human-in-the-Loop feature — a declarative approval affordance.

A fleet worker authors an allow-listed ``approval_card`` generative-UI intent
(operator can approve/deny/edit a pending action). The run plane projects it to
a stock ``CUSTOM`` frame (``name="cao.generative_ui"``). Unknown/unsafe
components would be refused by CAO's allow-list — only the closed vocabulary of
named components with JSON props is ever emitted (no HTML, no script).

For the *bidirectional* HITL round-trip against a live CLI permission prompt,
see ``interrupt.py`` (the flagship), which uses the full run-lifecycle interrupt
outcome + ``resume[]``.
"""

from __future__ import annotations

from fastapi import FastAPI, Request

from ._common import fleet_snapshot, make_bus, rec, run_response

_SESSION = "cao-human-in-the-loop"

_RECORDS = [
    rec(
        "launch",
        terminal_id="t-worker",
        session_name=_SESSION,
        detail={
            "agent_name": "developer",
            "provider": "mock_cli",
            "event_type": "post_create_terminal",
        },
    ),
    rec(
        "other",
        terminal_id="t-worker",
        session_name=_SESSION,
        ui={
            "component": "approval_card",
            "props": {
                "interrupt_id": "demo-hitl",
                "reason": "mock_cli:approval_request",
                "message": "Approve running the build step?",
                "options": ["approve", "deny", "edit"],
                "provider": "mock_cli",
                "terminal_id": "t-worker",
            },
        },
    ),
]

app = FastAPI(title="CAO — human_in_the_loop")


@app.post("/")
async def run(request: Request):
    return await run_response(
        request,
        snapshot_fn=fleet_snapshot,
        bus_subscribe_fn=make_bus(_RECORDS),
    )
