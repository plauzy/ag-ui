# CLI Agent Orchestrator (CAO) — AG-UI (Python)

CAO ([github.com/awslabs/cli-agent-orchestrator](https://github.com/awslabs/cli-agent-orchestrator))
already ships an AG-UI-compliant run plane. This directory does not
re-implement it — it provides a **keyless example server** that projects CAO's
merged run plane (`cli_agent_orchestrator.services.agui.run_plane`) into the
AG-UI Dojo over a deterministic `mock_cli` fleet.

- **No adapter code.** The server calls CAO's own `run_plane_stream` with
  keyless fixtures; CAO's official `EventEncoder` produces every frame.
- **Standalone.** It depends only on the published `cli-agent-orchestrator[agui]`
  extra (`ag-ui-protocol>=0.1.19,<0.2.0`) — never on a CAO source checkout — so
  there is no cross-repo drift.

See [`examples/`](./examples) to run the server and the contract tests.

The paired thin client is [`@ag-ui/cli-agent-orchestrator`](../typescript)
(`CliAgentOrchestratorAgent extends HttpAgent`).
