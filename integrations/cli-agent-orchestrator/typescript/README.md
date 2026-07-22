# @ag-ui/cli-agent-orchestrator

AG-UI client for [CLI Agent Orchestrator (CAO)](https://github.com/awslabs/cli-agent-orchestrator).

CAO runs each coding agent (Kiro CLI, Claude Code, Codex, …) as a **real OS
process** in an isolated tmux session and coordinates them supervisor → worker
over MCP. It exposes an AG-UI-compliant run plane (`POST /agui/v1/run`) that
emits official `ag-ui-protocol` `EventEncoder` frames — so this package is a
**thin `HttpAgent` subclass with zero extra wire code**.

## Install

```sh
pnpm add @ag-ui/cli-agent-orchestrator @ag-ui/client
```

## Usage

```ts
import { CliAgentOrchestratorAgent } from "@ag-ui/cli-agent-orchestrator";

const agent = new CliAgentOrchestratorAgent({
  url: "http://localhost:8024/agui/v1/run",
});

agent
  .run({
    threadId: "t1",
    runId: "r1",
    state: {},
    messages: [],
    tools: [],
    context: [],
    forwardedProps: {},
  })
  .subscribe((event) => console.log(event.type));
// RUN_STARTED -> STATE_SNAPSHOT -> ... -> RUN_FINISHED
```

On a live permission prompt, CAO closes the run with an **interrupt** outcome
(`RUN_FINISHED outcome={type:"interrupt", interrupts:[…]}`); answer it by
re-running with a `resume[]` entry
(`{ interruptId, status: "resolved", payload: { approved: true } }`, or
`{ interruptId, status: "cancelled" }` to deny), which CAO resolves idempotently
against the waiting CLI process.

## Why a bare subclass?

CAO's run plane already speaks stock AG-UI (official `EventEncoder`,
lifecycle-legal frame order, interrupt outcome + `resume[]`). The stock
`@ag-ui/client` transport consumes it directly, so there is no CAO-specific
protocol code here — that is the design invariant, enforced by a unit test.

See the [server example](../python/examples) for a keyless multi-feature Dojo
server, and CAO's [`docs/agui.md`](https://github.com/awslabs/cli-agent-orchestrator/blob/main/docs/agui.md)
for the full surface.

## License

MIT
