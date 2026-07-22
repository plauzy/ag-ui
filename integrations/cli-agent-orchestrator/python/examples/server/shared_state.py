"""Shared State feature — fleet STATE_SNAPSHOT + RFC-6902 STATE_DELTA.

Demonstrates CAO's read path: the run plane emits a fleet ``STATE_SNAPSHOT`` on
open, then a ``file_mod`` from the fleet is projected to an RFC-6902
``STATE_DELTA`` (an ``add`` on ``/last_file_mod``). Metadata only — no file
bodies on the wire.
"""

from __future__ import annotations

from fastapi import FastAPI, Request

from ._common import fleet_snapshot, make_bus, rec, run_response

_SESSION = "cao-shared-state"

_RECORDS = [
    rec(
        "file_mod",
        terminal_id="t-worker",
        session_name=_SESSION,
        detail={
            "path": "build/output.txt",
            "event_type": "file_modified",
        },
    ),
]

app = FastAPI(title="CAO — shared_state")


@app.post("/")
async def run(request: Request):
    return await run_response(
        request,
        snapshot_fn=fleet_snapshot,
        bus_subscribe_fn=make_bus(_RECORDS),
    )
