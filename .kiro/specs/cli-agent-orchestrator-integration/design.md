# Design — CLI Agent Orchestrator (CAO) AG-UI Integration

## 1. Guiding principle: thin projection, not re-implementation

CAO already ships a complete, merged AG-UI surface (pinned commit
`edf61cad65a8183d37466f2d112d19a365cfca5c`, PRs #485/#458). This integration is
a **thin projection** of that surface into the AG-UI monorepo + Dojo. The design
bias throughout is: *if you are writing protocol logic here, you have misread the
CAO contract.* The stock `HttpAgent` already speaks CAO's run plane; our job is
packaging, wiring, keyless example serving, tests, and narrative.

```
┌──────────────────────────── ag-ui monorepo (this PR) ─────────────────────────────┐
│  integrations/cli-agent-orchestrator/                                              │
│    typescript/   → @ag-ui/cli-agent-orchestrator                                   │
│                    class CliAgentOrchestratorAgent extends HttpAgent {}  (R2)      │
│    python/       → keyless example server (mock_cli), 4 feature endpoints (R3)     │
│    ARCHITECTURE.md                                                                 │
│  apps/dojo/…     → menu/agents/env/files/content-json wiring (R4)                  │
│  apps/dojo/e2e/tests/caoTests/*.spec.ts  → 4 asserting specs (R5)                  │
│  docs/…, CODEOWNERS, config-allowlist    → docs + governance (R7)                  │
└────────────────────────────────────────────────────────────────────────────────────┘
                                   │  HTTP (stock AG-UI wire)
                                   ▼
        CAO @ pinned commit  —  POST /agui/v1/run (EventEncoder frames)
                                 POST /agui/v1/interrupts/{id}/resume
                                 GET  /agui/v1/stream (ambient, used for dogfood evidence)
                                 gated by CAO_AGUI_ENABLED · needs [agui] extra
```

## 2. Directory layout (mirror `integrations/aws-strands/`)

```
integrations/cli-agent-orchestrator/
├── ARCHITECTURE.md
├── typescript/
│   ├── package.json                # @ag-ui/cli-agent-orchestrator
│   ├── tsconfig.json
│   ├── tsdown.config.ts
│   ├── README.md
│   └── src/
│       ├── index.ts                # exports CliAgentOrchestratorAgent
│       └── __tests__/
│           ├── cli-agent-orchestrator-agent.test.ts
│           └── docs-canonical-links.test.ts
└── python/
    ├── README.md
    └── examples/
        ├── README.md
        ├── pyproject.toml          # pins cli-agent-orchestrator[agui]
        └── server/
            ├── __init__.py
            ├── agentic_chat.py
            ├── shared_state.py
            ├── human_in_the_loop.py
            └── interrupt.py        # flagship
```

Rationale: `aws-strands` is the closest analog (an AWS integration with both a
Python reference server and a TS client). Following its shape minimizes reviewer
surprise and reuses its `tsdown`/`vitest`/`publint`/`attw` conventions.

## 3. TypeScript thin client (R2)

`src/index.ts` — the entire client:

```ts
import { HttpAgent } from "@ag-ui/client";

/**
 * AG-UI client for CLI Agent Orchestrator (CAO).
 * Points at CAO's stock run plane (POST /agui/v1/run), which emits official
 * ag-ui-protocol EventEncoder frames — so no extra wire code is required.
 * See github.com/awslabs/cli-agent-orchestrator (docs/agui.md).
 */
export class CliAgentOrchestratorAgent extends HttpAgent {}
```

- **package.json** — mirror `@ag-ui/aws-strands`: `build: tsdown`, `test: vitest run`,
  `test:exports: publint --strict && attw --pack`, `typecheck: tsc --noEmit`;
  peerDeps `@ag-ui/client|core|encoder` (workspace devDeps); MIT; `publishConfig.access=public`.
- **No `/server` subpath** is needed (the example server is Python), unlike
  aws-strands. Keep `exports` to the single entry to keep browser bundlers clean.

**Why a bare subclass and not more:** CAO's run plane already produces
lifecycle-legal stock frames (`RUN_STARTED`→`STATE_SNAPSHOT`→…→`RUN_FINISHED`,
interrupt outcome + `resume[]`) via the official `EventEncoder`. `HttpAgent`
consumes exactly that. Adding logic here would fork the contract.

## 4. Keyless example server (R3)

Python FastAPI app under `python/examples/server/`, one module per feature,
each mounting a route that drives a CAO `mock_cli` fleet with the AG-UI surface
enabled (`CAO_AGUI_ENABLED=1`). The Dojo TS client targets these via `caoUrl`.

| Endpoint | Feature | What it exercises |
|---|---|---|
| `/agentic_chat` | `agentic_chat` | Baseline run: `RUN_STARTED`→projection→`RUN_FINISHED` over a mock CLI turn |
| `/shared_state` | `shared_state` | Fleet `STATE_SNAPSHOT` + RFC-6902 `STATE_DELTA` folding (read path) |
| `/human_in_the_loop` | `human_in_the_loop` | Approval affordance surfaced from fleet activity |
| `/interrupt` | `interrupt` **(flagship)** | Real mock permission prompt → `RUN_FINISHED outcome={type:"interrupt"}` → `resume[]` round-trip |

Design constraints:
- **Keyless:** `mock_cli` provider — no provider API keys, deterministic output,
  runs anywhere CI runs (satisfies R3.1/R5.3).
- **Standalone:** `pyproject.toml` pins `cli-agent-orchestrator[agui]==<pinned>`
  (matching the pinned commit's release) plus `uvicorn`. No source dependency on
  the CAO checkout → no cross-repo drift (R3.5).
- **Port 8024, `/health`, CORS** per upstream server conventions (R3.4).
- The server is a **thin composition** over CAO's `POST /agui/v1/run` +
  `POST /agui/v1/interrupts/{id}/resume`; it must not reimplement the encoder or
  interrupt registry (those are CAO's, at the pinned commit).

### Flagship interrupt flow (the differentiator made concrete)

```
Dojo (CliAgentOrchestratorAgent) --POST /agui/v1/run--> CAO mock_cli fleet
   fleet worker hits a mock permission prompt
CAO --RUN_FINISHED outcome={type:"interrupt", interrupts:[{id, reason:"mock_cli:permission_request", …}]}-->
   Dojo renders approve/deny affordance
Dojo --POST /agui/v1/run { resume:[{approved:true}] }--> CAO
   CAO resolves via idempotent approval registry, resumes the run --RUN_FINISHED success-->
```

This is the thing no API-wrapper integration can show: an actual (mock, but
real-path) CLI permission prompt approved from the browser through AG-UI's
standard interrupt lifecycle.

## 5. Dojo wiring (R4)

Concrete edits, matching the existing patterns read from the Dojo source:

- **`apps/dojo/src/menu.ts`** — append (single source of truth):
  ```ts
  { id: "cli-agent-orchestrator", name: "CLI Agent Orchestrator (CAO)",
    features: ["agentic_chat", "shared_state", "human_in_the_loop", "interrupt"] }
  ```
- **`apps/dojo/src/env.ts`** — add `caoUrl: string` to the type and
  `caoUrl: process.env.CAO_URL || "http://localhost:8024"` to the return.
- **`apps/dojo/src/agents.ts`** — import `CliAgentOrchestratorAgent`, add a
  `"cli-agent-orchestrator"` factory using `mapAgents` against `${envVars.caoUrl}/${path}`
  for the four features (the `interrupt` agent may pass `debug: true` like the
  strands HITL agent).
- **`apps/dojo/package.json`** — add `"@ag-ui/cli-agent-orchestrator": "workspace:*"`.
- **`apps/dojo/src/files.json`** + **`scripts/generate-content-json.ts`** — map
  the CAO feature source files so they render in the Dojo code viewer
  (generate-content-json reads `menuIntegrations`, so the menu entry drives it;
  add file paths for the four Python feature modules).
- **`scripts/prep-dojo-everything.js`** / **`run-dojo-everything.js`** — add the
  CAO server to the local orchestration (prep installs the example server's
  deps; run launches it on 8024 before the Dojo) — additive only.

## 6. Shift-left testing strategy (R5)

Layered, all fail-closed:

1. **TS unit (`vitest`)**
   - `cli-agent-orchestrator-agent.test.ts` — asserts `CliAgentOrchestratorAgent`
     is an `HttpAgent` subclass and constructs with a `url` (contract smoke).
   - `docs-canonical-links.test.ts` — scans shipped Markdown; FAILS on any
     non-canonical CAO URL (e.g. a fork URL). Guards R7.1 permanently.
2. **Playwright e2e (`apps/dojo/e2e/tests/caoTests/`)** — four specs
   (`agenticChatPage`, `sharedStatePage`, `humanInTheLoopPage`, `interruptPage`).
   Each drives the live keyless server through the Dojo and asserts a **rendered
   outcome**. `interruptPage.spec.ts` asserts the full approve (and deny) path
   completes, not merely that a card appears.
3. **CI matrix (`.github/workflows/dojo-e2e.yml`)** — a `cli-agent-orchestrator`
   entry that boots the Python example server (keyless) + runs the four specs.
   No secrets → the matrix stays green-or-red on the contract alone.
4. **Backing demo GIFs** — sourced from CAO's `examples/ag-ui/ag-ui-construct-demos`
   recorder at the pinned commit, which produces a GIF **only** when the backing
   asserting example prints its `PASS` marker. Referenced in the PR body via the
   canonical CAO raw URLs; never hand-made.

**Fail-closed matrix:**

| Contract that could drift | Caught by |
|---|---|
| CAO run-plane frame shape changes | e2e specs (render assertions) go red |
| Fork/non-canonical URL leaks into docs | `docs-canonical-links.test.ts` fails |
| Client adds non-standard wire code | `cli-agent-orchestrator-agent.test.ts` + `attw`/`publint` |
| Example server needs a secret | CI matrix fails (keyless invariant) |
| A backing construct regresses | CAO recorder refuses to emit a GIF (no green demo) |

## 7. Dogfooding strategy (R6)

- **Evidence:** the PR uses CAO's `ag-ui-meta-dogfood` capture — a genuine
  supervisor→developer→reviewer cross-provider fleet (`kiro_cli`, `claude_code`,
  `codex`) recorded on the live `GET /agui/v1/stream` under only
  `CAO_AGUI_ENABLED`, with the metadata-only privacy boundary asserted in its
  `timeline.json`. This is the "the audit fleet visualizes itself" proof and
  directly demonstrates differentiators #1, #2, and #5.
- **Process:** the integration itself should be built by a CAO fleet
  (supervisor→worker over MCP) where the environment allows — making the PR an
  instance of the capability it ships. If the sandbox cannot run a real fleet,
  the spec/tasks are authored so a CAO fleet *can* execute them unmodified.

## 8. Differentiator narrative placement

The conviction (requirements § Differentiators) lands in three artifacts so a
visitor meets it at any depth:
- **`ARCHITECTURE.md`** — the full L1/L2/L3 construct model + the "empty axis"
  positioning (CAO = real processes **and** protocol).
- **`docs/introduction.mdx` + `docs/integrations.mdx`** — one-line positioning:
  the first AG-UI source driving real CLI coding-agent processes with genuine
  permission-prompt interrupts.
- **The `interrupt` Dojo feature** — the interactive proof of differentiator #3.

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| CAO contract drift after the pinned commit | Pin every reference to `edf61cad…`; `docs-canonical-links` + e2e catch drift |
| Cross-repo coupling | Example server depends only on the published `[agui]` extra, not the CAO checkout |
| Governance ambiguity (AG-UI is CopilotKit-stewarded) | Scope is additive + version-pinned to a single SDK range (`ag-ui-protocol>=0.1.19,<0.2.0`) |
| Reviewer wants smaller PRs | Natural split documented in tasks: (a) TS client, (b) example server, (c) Dojo wiring + e2e, (d) docs |
| Prior PR #2216 already open | This spec finalizes/supersedes it; reconcile against its file list before pushing |

## 10. Definition of done
All of requirements R1–R8 satisfied; four e2e specs green in CI without secrets;
CAO renders in the Dojo with a working interrupt round-trip; PR body carries the
differentiator narrative + dogfood evidence and states "Fixes #2215".
