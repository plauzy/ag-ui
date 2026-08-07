# Requirements — CLI Agent Orchestrator (CAO) AG-UI Integration

## Purpose

Add [awslabs/cli-agent-orchestrator](https://github.com/awslabs/cli-agent-orchestrator)
(CAO) as a **first-class AG-UI integration** rendered in the Dojo, and land the
official integration PR that closes out
[ag-ui-protocol/ag-ui#2215](https://github.com/ag-ui-protocol/ag-ui/issues/2215)
(tracked by the open draft
[ag-ui-protocol/ag-ui#2216](https://github.com/ag-ui-protocol/ag-ui/pull/2216)).

This spec **grounds the implementing agent in the latest merged CAO sources of
truth** so the integration is a faithful, drift-free projection of what CAO
already ships — not a re-implementation.

## Sources of truth (pinned)

The integration is a thin client + example server over CAO's already-merged
AG-UI surface. Do **not** invent protocol behavior; mirror these:

| Source | Reference | What it establishes |
|---|---|---|
| CAO AG-UI Phase 2 (L2 constructs + run plane) | `awslabs/cli-agent-orchestrator` @ **`edf61cad65a8183d37466f2d112d19a365cfca5c`** (PRs #485/#458) | The endpoints, wire dialects, interrupt lifecycle, and privacy boundary this integration projects |
| CAO AG-UI Phase 0–1 (L1 adapter) | PR #436 (merged) | `GET /agui/v1/stream`, `emit_ui`, 6-component allow-list, `STATE_SNAPSHOT`/RFC-6902 `STATE_DELTA` |
| CAO proposal / differentiators | issue #386 | The unique-value conviction (§ Differentiators below) |
| CAO AG-UI reference doc | `docs/agui.md` @ pinned commit | Ambient vs run plane, replay contract, generative-UI safety model |
| Prior integration PR | `ag-ui-protocol/ag-ui#2216` | The intended file surface + Dojo wiring shape |
| Reference integration to mirror | `integrations/aws-strands/` (this repo) | Directory shape, TS thin-client + example-server conventions |
| Protocol overview | https://docs.ag-ui.com/introduction | Wire semantics the integration must honor |

**Determinism rule:** every reference to CAO behavior in design/tasks MUST cite
the pinned commit above (not a moving branch tip). If a task needs CAO code that
is not present at that commit, stop and flag it rather than assuming a newer
commit.

## The CAO AG-UI surface this integration consumes (verbatim contract)

Established at the pinned commit; the integration relies on **only** these:

- **Ambient plane** — `GET /agui/v1/stream` (SSE, CAO dialect: `event:`+`data:`
  UPPER_SNAKE frames, `id:` cursor, replay via `Last-Event-ID`/`?since=`).
- **Stock run plane** — `POST /agui/v1/run` accepts a stock `RunAgentInput`
  (camelCase) and streams lifecycle-legal frames via the official
  `ag-ui-protocol` `EventEncoder` (`data:`-only camelCase, `type` field):
  `RUN_STARTED` → `STATE_SNAPSHOT` → projection frames → `RUN_FINISHED`.
  On open interrupts it closes with `RUN_FINISHED outcome={type:"interrupt", interrupts:[…]}`.
- **Interrupt resume** — client re-POSTs `/agui/v1/run` with a `resume[]` array,
  or calls `POST /agui/v1/interrupts/{id}/resume` (idempotent, exactly-once).
- **Enablement + packaging** — surface is default-off behind `CAO_AGUI_ENABLED`;
  the run plane requires the `cli-agent-orchestrator[agui]` extra
  (`ag-ui-protocol>=0.1.19,<0.2.0`). Missing extra → HTTP 501; disabled → 404.
- **Privacy boundary** — metadata-only; message bodies never on the wire.

## Differentiators (the conviction this integration must showcase)

Per issue #386, CAO occupies the empty axis between multi-CLI orchestrators
(real processes, no protocol) and AG-UI frameworks (protocol, no real
processes). The integration and its demo MUST make these legible to a Dojo
visitor. Content rephrased for compliance:

1. **Real-process agent runtime.** Every other AG-UI source assumes an
   addressable HTTP agent already exists. CAO runs each coding agent as a real
   OS process in an isolated tmux session and exposes that lifecycle through the
   protocol.
2. **One stream over N heterogeneous CLI runtimes.** Existing integrations are
   single-framework. CAO fronts Kiro CLI, Claude Code, Codex, … over one
   normalized stream; a new provider joins with zero protocol code.
3. **Permission prompts as standard interrupts.** CLI agents pause on
   trust/permission prompts constantly. CAO maps that onto AG-UI's interrupt
   lifecycle with provider-namespaced reasons and approve/deny/edit resume —
   something no API-wrapper integration can demonstrate.
4. **Fleet semantics + construct programming model.** Supervisor→worker
   hierarchy, delegation timelines, and cross-provider state, exposed as typed,
   subclassable L2 constructs (CDK-style L1/L2/L3), not a one-off adapter.
5. **Privacy-bounded observability.** Metadata-only streaming, asserted by
   tests — fleet observability without conversation leakage.

## Requirements (EARS)

### R1 — Directory & packaging parity
- **R1.1** The integration SHALL live at
  `integrations/cli-agent-orchestrator/` with `python/`, `typescript/`, and an
  `ARCHITECTURE.md`, mirroring `integrations/aws-strands/`.
- **R1.2** WHEN the TypeScript package is built, the package SHALL be named
  `@ag-ui/cli-agent-orchestrator`, build with `tsdown`, test with `vitest`, and
  pass `publint --strict` + `attw` via a `test:exports` script.
- **R1.3** The TS package SHALL declare `@ag-ui/client`, `@ag-ui/core`,
  `@ag-ui/encoder` as peer dependencies (workspace devDeps), matching repo
  convention.

### R2 — Thin client (zero extra wire code)
- **R2.1** The package SHALL export `class CliAgentOrchestratorAgent extends HttpAgent {}`
  from `@ag-ui/client`, pointed at CAO's `POST /agui/v1/run` endpoint, with no
  bespoke protocol/transport code.
- **R2.2** IF CAO adds no non-standard wire behavior, THEN the client SHALL add
  none either (any deviation is a signal the CAO contract was misread).

### R3 — Keyless example server (Dojo features)
- **R3.1** The example server SHALL use CAO's `mock_cli` fleet so it runs with
  **no external API keys** (the entire e2e matrix must run secret-free in CI).
- **R3.2** The server SHALL expose the four standard features on discrete
  endpoints: `agentic_chat`, `shared_state`, `human_in_the_loop`, and the
  flagship `interrupt`.
- **R3.3** WHEN a real (mock) permission prompt occurs during `interrupt`, the
  server SHALL surface `RUN_FINISHED outcome={type:"interrupt"}` and resolve via
  a `resume[]` re-POST — a genuine round-trip, not a simulated banner.
- **R3.4** The server SHALL listen on port **8024**, expose `/health`, and set
  CORS per upstream convention.
- **R3.5** The server SHALL be standalone — depending only on the pinned
  `cli-agent-orchestrator[agui]` extra — so there is **no cross-repo drift risk**.

### R4 — Dojo wiring
- **R4.1** The integration SHALL register in `apps/dojo/src/menu.ts` (id
  `cli-agent-orchestrator`, features: the four in R3.2) as the single source of
  truth for the UI/proxy/agents validation.
- **R4.2** `apps/dojo/src/agents.ts` SHALL construct `CliAgentOrchestratorAgent`
  instances against a new `caoUrl` env var, and `apps/dojo/src/env.ts` SHALL add
  `caoUrl` defaulting to `http://localhost:8024`.
- **R4.3** `apps/dojo/package.json` (workspace dep), `files.json`,
  `scripts/generate-content-json.ts`, `scripts/prep-dojo-everything.js`, and
  `scripts/run-dojo-everything.js` SHALL be updated so the integration renders
  and its source files display in the Dojo.

### R5 — Shift-left testing (proof-of-work, not decoration)
- **R5.1** The TS client SHALL ship `vitest` unit tests, including a
  `docs-canonical-links.test.ts` that FAILS if any shipped Markdown references a
  non-canonical CAO URL (guarding against fork-URL drift).
- **R5.2** Four Playwright e2e specs SHALL live under
  `apps/dojo/e2e/tests/caoTests/` — one per feature — and SHALL assert real
  rendered outcomes (the `interrupt` spec asserts the approve/deny round-trip),
  not just page loads.
- **R5.3** A CI matrix entry in `.github/workflows/dojo-e2e.yml` SHALL run the
  keyless CAO server + the four specs without secrets.
- **R5.4** Every asserting artifact SHALL fail closed: a broken contract turns
  CI red; a green run is evidence the contract holds. Demo GIFs referenced in
  the PR are produced by CAO's `ag-ui-construct-demos` recorder, which emits a
  GIF **only** on the backing example's PASS marker.

### R6 — Dogfooding (the change demonstrates the thing it ships)
- **R6.1** The PR narrative SHALL use CAO's own `ag-ui-meta-dogfood` capture —
  a real supervisor→developer→reviewer cross-provider fleet (`kiro_cli`,
  `claude_code`, `codex`) observed on the live `GET /agui/v1/stream` — as the
  real-provider evidence that the surface works end-to-end under the production
  path with the privacy boundary intact.
- **R6.2** WHERE feasible, the integration work itself SHALL be produced by a
  CAO fleet (supervisor→worker over MCP), so the deliverable is an instance of
  the capability it documents.

### R7 — Docs & governance
- **R7.1** `docs/integrations.mdx` and `docs/introduction.mdx` SHALL list CAO,
  and READMEs (TS + Python) SHALL reference the canonical
  `github.com/awslabs/cli-agent-orchestrator` repo.
- **R7.2** `.github/CODEOWNERS` and `.github/config-allowlist.txt` SHALL be
  updated for the new integration directory.

### R8 — Additivity & no regressions
- **R8.1** The change SHALL be strictly additive: no existing integration,
  Dojo feature, or CI job behavior changes.
- **R8.2** WHEN the CAO example server is absent, the Dojo build and all other
  integrations SHALL be unaffected.

## Out of scope
- Hosting a live multi-agent demo server on the public Dojo (tmux/Docker) —
  deferred to a maintainer-side follow-up, as noted in issue #2215.
- Changes to CAO core (the surface is already merged at the pinned commit).
- New AG-UI protocol events or SDK changes.

## Acceptance
The spec is satisfied when the PR in R-scope: (a) mirrors the pinned CAO
contract exactly, (b) runs keyless in CI with four asserting e2e specs green,
(c) renders CAO in the Dojo with a working interrupt round-trip, (d) carries the
differentiator narrative + dogfood evidence, and (e) closes issue #2215.
