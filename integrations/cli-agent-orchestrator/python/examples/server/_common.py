"""Shared helpers for the keyless CAO AG-UI example server.

Every feature route is a thin call into CAO's *merged* run plane
(``cli_agent_orchestrator.services.agui.run_plane.run_plane_stream``) with
keyless, deterministic fixtures — no tmux, no providers, no API keys. The run
plane is the single authority for frame shape and the interrupt lifecycle; this
module only supplies the fleet fixtures a real CAO server would supply from live
processes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from fastapi import Request
from fastapi.responses import StreamingResponse

from cli_agent_orchestrator.services.agui.run_plane import (
    AG_UI_AVAILABLE,
    get_run_plane_content_type,
    run_plane_stream,
)

CANONICAL_REPO = "https://github.com/awslabs/cli-agent-orchestrator"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rec(
    kind: str,
    *,
    terminal_id: Optional[str] = None,
    session_name: str = "cao-demo",
    detail: Optional[Dict[str, Any]] = None,
    ui: Optional[Dict[str, Any]] = None,
    record_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a CAO event record in the exact shape ``to_agui_event`` consumes.

    The six-primitive vocabulary (``launch | completion | handoff |
    a2a_delegation | file_mod | error``) plus an optional agent-authored ``ui``
    intent is all the L1 adapter reads. Message bodies are never included — the
    privacy boundary is inherited from the mapper by construction.
    """
    record: Dict[str, Any] = {
        "id": record_id or str(uuid.uuid4()),
        "kind": kind,
        "timestamp": now_iso(),
        "session_name": session_name,
        "terminal_id": terminal_id,
        "detail": detail or {},
    }
    if ui is not None:
        record["ui"] = ui
    return record


def make_bus(records: List[Dict[str, Any]]) -> Callable[[], AsyncGenerator[Dict[str, Any], None]]:
    """Return a zero-arg async-iterator factory yielding ``records`` then stopping.

    Matches the ``bus_subscribe_fn`` contract of ``run_plane_stream``: a callable
    returning an async iterator of live CAO event records. When exhausted, the
    run plane emits ``RUN_FINISHED`` (success).
    """

    async def _subscribe() -> AsyncGenerator[Dict[str, Any], None]:
        for record in records:
            yield record

    return _subscribe


async def run_response(request: Request, **run_kwargs: Any) -> StreamingResponse:
    """Stream ``run_plane_stream`` for one request as a stock AG-UI SSE response."""
    body = await request.json()
    accept = request.headers.get("accept")
    # Short heartbeat is irrelevant for finite fixtures but keeps the demo snappy.
    run_kwargs.setdefault("heartbeat_interval", 30.0)
    return StreamingResponse(
        run_plane_stream(body, accept=accept, **run_kwargs),
        media_type=get_run_plane_content_type(accept),
    )


def fleet_snapshot() -> Dict[str, Any]:
    """A deterministic fleet ``STATE_SNAPSHOT`` payload (metadata only)."""
    return {
        "sessions": [{"name": "cao-demo", "provider_mix": ["mock_cli"]}],
        "terminals": [
            {
                "terminal_id": "t-supervisor",
                "agent_name": "code_supervisor",
                "provider": "mock_cli",
                "status": "running",
            },
            {
                "terminal_id": "t-worker",
                "agent_name": "developer",
                "provider": "mock_cli",
                "status": "running",
            },
        ],
        "last_file_mod": None,
    }


__all__ = [
    "AG_UI_AVAILABLE",
    "CANONICAL_REPO",
    "fleet_snapshot",
    "make_bus",
    "rec",
    "run_response",
]
