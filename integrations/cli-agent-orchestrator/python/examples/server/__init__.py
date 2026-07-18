"""
CLI Agent Orchestrator dojo example server for the AG-UI protocol.

Demonstrates agentic chat, shared state, human-in-the-loop,
and the interrupt/approval lifecycle without requiring a real CAO backend.
"""

import os
import uvicorn
from fastapi import FastAPI
from .agentic_chat import agentic_chat_endpoint
from .shared_state import shared_state_endpoint
from .human_in_the_loop import human_in_the_loop_endpoint
from .interrupt import interrupt_endpoint

app = FastAPI(title="CLI Agent Orchestrator - AG-UI Dojo Server")

# Register endpoints with hyphenated paths matching agents.ts path mappings
app.post("/agentic-chat")(agentic_chat_endpoint)
app.post("/shared-state")(shared_state_endpoint)
app.post("/human-in-the-loop")(human_in_the_loop_endpoint)
app.post("/interrupt")(interrupt_endpoint)


def main():
    """Run the uvicorn server."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host=host, port=port, reload=True)
