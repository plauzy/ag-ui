# CLI Agent Orchestrator (CAO) × AG-UI — Architecture

This integration renders a **live multi-agent fleet of real CLI coding agents**
through AG-UI. It is a thin projection of a surface CAO already ships upstream
(awslabs/cli-agent-orchestrator#458, merged) — not a re-implementation.

## Why CAO is a different kind of AG-UI source

Every other integration in this repo binds **one framework** to the protocol and
assumes an addressable HTTP agent already exists. CAO sits on the empty axis
between multi-CLI orchestrators (real processes, no protocol) and AG-UI
frameworks (protocol, no real processes). It brings, net-new to the ecosystem:

1. **A real-process agent runtime.** CAO spawns, persists, resumes, and
   multiplexes long-lived CLI agent processes (tmux-backed), then exposes that
   lifecycle through AG-UI. No other AG-UI source manages real OS processes.
2. **One stream over N heterogeneous runtimes.** Kiro CLI, Claude Code, and
   Codex all speak the same normalized stream; a new provider joins by
   implementing one base interface — zero protocol code.
3. **Permission prompts as standard interrupts.** CLI agents pause on
   trust/permission prompts constantly. CAO maps that onto AG-UI's interrupt
   lifecycle with provider-namespaced reasons (`claude-code:permission_request`,
   `kiro:trust_prompt`) and approve / deny / edit `resume[]`. This is the
   flagship demo — something no API-wrapper integration can show.
4. **Fleet semantics as a construct programming model.** Supervisor→worker
   hierarchy, delegation timelines, and cross-provider shared state, exposed as
   typed, subclassable L2 constructs (CDK-style L1/L2/L3) rather than a one-off
   adapter.
5. **A privacy-bounded observability posture.** Metadata-only streaming —
   message bodies never on the wire, asserted by tests.

## Layers

```
L3  Composed surfaces (dashboards, team control planes)   [downstream]
L2  Named, subclassable constructs                        [awslabs/cli-agent-orchestrator#458]
      SupervisorDashboardStream · MultiAgentSessionTimeline
      AgentHandoffWithApproval · CrossProviderStateSync
L1  Raw protocol adapter (one pure module, default-off)   [#436]
      services/agui_stream.py  → CAO primitives → AG-UI typed events
      GET  /agui/v1/stream      (ambient SSE, CAO dialect)
      POST /agui/v1/run         (stock EventEncoder frames + interrupt/resume)
L0  Existing CAO substrate (unchanged)
      event bus · event_primitives · ui_state_service · tmux terminals · providers
```

## What this directory ships

```
typescript/   @ag-ui/cli-agent-orchestrator — `CliAgentOrchestratorAgent extends HttpAgent`
              (zero extra wire code; consumes CAO's stock run plane directly)
python/       keyless example server driving CAO's `mock_cli` fleet through
              run_plane_stream, exposing four Dojo features on port 8024:
                agentic_chat · shared_state · human_in_the_loop · interrupt (flagship)
```

## Wire contract (consumed, not re-implemented)

The example server calls CAO's merged `run_plane_stream`
(`cli_agent_orchestrator.services.agui.run_plane`) with keyless, deterministic
fixtures. That function is the single authority for frame shape and the
interrupt lifecycle:

- `RUN_STARTED` → `STATE_SNAPSHOT` → projection frames → `RUN_FINISHED`
- Open interrupt → `RUN_FINISHED outcome={type:"interrupt", interrupts:[…]}`
- Client answers via `resume:[{ interruptId, payload }]` (idempotent,
  exactly-once resolution).

Because the server reuses CAO's own encoder + interrupt registry, there is no
cross-repo drift: it depends only on the published `cli-agent-orchestrator[agui]`
extra (`ag-ui-protocol>=0.1.19,<0.2.0`), never on a CAO source checkout.

## Keyless by construction

The `mock_cli` fleet needs no external API keys and no real tmux/browser, so the
example server and the whole e2e/CI path run secret-free. The features emit
**fleet-lifecycle** frames (not LLM chat), which is the point: this integration
showcases orchestration and interrupts, not another chat wrapper.

## References

- CAO AG-UI surface & docs: https://github.com/awslabs/cli-agent-orchestrator/blob/main/docs/agui.md
- Phase 2 (L2 constructs + run plane): awslabs/cli-agent-orchestrator#458
- Phase 0–1 (L1 adapter): awslabs/cli-agent-orchestrator#436
