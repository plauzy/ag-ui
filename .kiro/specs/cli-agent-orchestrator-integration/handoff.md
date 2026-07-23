# Handoff — CAO × AG-UI integration: differentiators, worker prompt, and PR lede

This is a single, self-contained handoff for a local Kiro worker taking over the
official CAO AG-UI Dojo integration. It consolidates: (1) the conviction — what
makes this integration unique; (2) a ready-to-paste worker prompt with the
roadmap-alignment mapping; and (3) a maintainer-facing PR lede to adapt.

**Ground truth (pinned):** CAO @ `awslabs/cli-agent-orchestrator`
`edf61cad65a8183d37466f2d112d19a365cfca5c` (AG-UI Phase 2, PRs #485/#458).
Canonical URLs only. Closes `ag-ui-protocol/ag-ui#2215`; supersedes/reconciles
`#2216`. Read `requirements.md` / `design.md` / `tasks.md` in this directory
first. Fork PRs: `plauzy/ag-ui#4` (this spec) · `plauzy/ag-ui#5`
(implementation, branch `feat/cao-agui-integration`).

---

## 1. What separates this integration from every other one

Every other AG-UI source binds **one framework** to the protocol and assumes an
addressable HTTP agent already exists. CAO fills the empty axis between multi-CLI
orchestrators (real processes, no protocol) and AG-UI frameworks (protocol, no
real processes).

| # | Differentiator | Why no other integration has it | How the demo must prove it (asserting artifact) |
|---|---|---|---|
| 1 | **Real-process agent runtime** | Others wrap an SDK/API; CAO spawns, persists, resumes, multiplexes long-lived CLI agents as OS processes (tmux) and exposes that lifecycle | Fleet lifecycle streamed live on `GET /agui/v1/stream` (the meta-dogfood capture) |
| 2 | **One stream over N heterogeneous CLIs** | Others are single-framework (LangGraph→AG-UI, Mastra→AG-UI…); CAO fronts Kiro CLI, Claude Code, Codex over one normalized vocabulary | `CrossProviderStateSync` across ≥3 providers rendering **uniformly** |
| 3 | **Permission prompts as standard interrupts** (FLAGSHIP) | No one has mapped a live CLI trust/permission prompt onto AG-UI's interrupt lifecycle | Approve **and** deny a real prompt from the browser: `RUN_FINISHED outcome=interrupt` → `resume[]` (status `resolved`/`cancelled`) |
| 4 | **A construct programming model, not an adapter** | Others ship a point adapter; CAO ships typed, subclassable L2 blocks (CDK-style L1/L2/L3) — a new provider joins with zero protocol/UI code | A surface composed purely from L2 constructs |
| 5 | **Privacy-bounded observability** | No integration draws this line | A test asserting message bodies never hit the wire |

**The thesis that ties it together (and that maintainers will care about):**
normalizing over N heterogeneous runtimes **without** coupling to their low-level
implementations is the scalable way to build multi-agent UIs — add a provider by
implementing one base interface, and it appears in every construct and every
AG-UI client for free. That makes CAO a live **reference implementation /
production testbed** for the AG-UI roadmap, not just another integration.

**Why we move fast:** provider abstraction only stays honest if a fail-closed
test proves the abstraction the moment it's written. Shift-left + dogfooding are
not ceremony — they are the mechanism. The demo is never a screenshot; it is an
asserting artifact that goes red the instant the contract drifts.

---

## 2. Worker prompt (paste verbatim)

```
# Task: Make the CAO × AG-UI integration DEMONSTRATE its differentiators and draw AG-UI maintainer attention

Context: implementation is in `plauzy/ag-ui` PR #5 (branch feat/cao-agui-integration),
spec at `.kiro/specs/cli-agent-orchestrator-integration/`, closing
ag-ui-protocol/ag-ui#2215 / superseding #2216. CAO source of truth is PINNED at
awslabs/cli-agent-orchestrator @ edf61cad… (canonical URLs only). Read the spec first.

Your job is NOT to add features — it is to make five differentiators *legible and
proven*, then package that as an upstream PR a maintainer cannot ignore. Adhere
strictly to our process: shift-left testing (every claim backed by a fail-closed
asserting artifact) and dogfooding (build it with the thing it ships).

## The five things the demo must prove (each needs an ASSERTING artifact, not a screenshot)
1. Real-process runtime — fleet lifecycle streamed live on GET /agui/v1/stream.
2. One stream over N heterogeneous CLIs — ≥3 providers (kiro_cli, claude_code,
   codex) rendering UNIFORMLY through the same constructs (CrossProviderStateSync).
3. Permission prompts as standard interrupts (FLAGSHIP) — approve AND deny a real
   permission prompt from the browser: RUN_FINISHED outcome=interrupt → resume[]
   (status "resolved"/"cancelled"). The one no API-wrapper integration can do.
4. Construct programming model — a surface composed purely from L2 constructs;
   a new provider joins with zero protocol/UI code. Show, don't assert prose.
5. Privacy boundary — a test proving message bodies never hit the wire.

## Hard process rules (non-negotiable — this is why we move fast)
- SHIFT-LEFT: for every differentiator above, there must be a keyless,
  fail-closed test that turns CI red on drift. The authoritative keyless proof is
  the Python contract suite (currently 7/7); extend it if a claim lacks a test.
  Demo GIFs are only produced by CAO's PASS-gated recorder — never hand-made.
- DOGFOOD: use CAO's own ag-ui-meta-dogfood capture (real supervisor→developer→
  reviewer cross-provider fleet on the live stream, privacy boundary intact) as
  the real-provider evidence, and — where feasible — build this PR with a CAO
  fleet and say so in the body ("built by the orchestrator it integrates").
- ABSTRACTION DISCIPLINE: the TS client stays a bare HttpAgent subclass; the
  server stays a thin projection over CAO's merged run_plane_stream. If you find
  yourself writing provider-specific or protocol wire code, you've broken the
  thesis — stop and reframe. The whole point is depending on the normalized
  vocabulary, not any provider's low-level implementation.
- CANONICAL URLS ONLY (awslabs/cli-agent-orchestrator); keep the
  docs-canonical-links guard green. Strictly additive; regenerate files.json and
  pnpm-lock.yaml properly; no build artifacts committed; pin CAO to edf61cad.

## Close the verification gap
Run the full local e2e (pnpm install → prep/run-dojo-everything for dojo +
cli-agent-orchestrator → the caoTests Playwright suite). Tune the specs so each
asserts a REAL rendered outcome; the interrupt spec MUST assert both approve and
deny complete end-to-end. Keep it keyless.

## Draw maintainer attention — the framing that lands
Position CAO in the upstream PR + a section in ARCHITECTURE.md NOT as "another
integration" but as the first real-process, multi-runtime REFERENCE IMPLEMENTATION
and production testbed for the AG-UI roadmap items that are hardest to validate.
Make the thesis explicit: normalizing over N heterogeneous runtimes WITHOUT
coupling to their low-level implementations is the scalable path for multi-agent
UIs — and CAO is the place to pressure-test it. Include this mapping verbatim:

  | On the AG-UI roadmap | What CAO brings to it |
  |---|---|
  | Sub-agents and composition (upcoming building block) | CAO's handoff/delegation model is a live, shipping composition system across heterogeneous agents — real-world input for the spec, and a first implementation the day it lands |
  | Interrupts / human-in-the-loop (draft: interrupt-aware run lifecycle) | CLI permission and trust prompts are the highest-volume HITL workload anywhere; CAO's provider-namespaced interrupt mapping exercises the draft at scale |
  | Agent steering (upcoming building block) | CAO already steers live agents mid-run (input injection, inbox delivery to running terminals) — steering semantics can be validated against real processes |
  | Tool output streaming (upcoming building block) | Terminal output is the ultimate streaming tool output; CAO's FIFO→event-bus pipeline is a ready-made torture test |
  | Shared state, read-write (upcoming building block) | CAO's fleet snapshot + RFC 6902 delta channel is a working read path; the L2 constructs define the write path |
  | Generative UI, declarative (draft proposal) | CAO's server-validated emit_ui component allow-list is a concrete, security-conscious take on declarative generative UI |
  | Background agents (showcased in the AG-UI Dojo) | Headless/scheduled CAO agents are background agents by construction |

For each row, link the concrete CAO capability/test/demo that exercises it, so the
claim is verifiable, not aspirational. Propose the partnership framing from #386
(ecosystem listing + a CAO-backed Dojo demo driving real CLI processes + co-design
of the fleet/interrupt/workspace conventions), and offer CODEOWNERS listing.

## Definition of done
Five differentiators each backed by a green, keyless, fail-closed artifact;
interrupt approve/deny proven in Playwright + pytest; dogfood evidence embedded
via canonical URLs; the roadmap-alignment table (above) in the PR with each row
linked to a verifiable artifact; official PR open against ag-ui-protocol/ag-ui
with "Fixes #2215", reconciled against #2216.
```

**Honesty guardrail for the worker:** several roadmap rows (steering, tool-output
streaming, the state *write* path, background agents) go beyond what PR #5 ships
tests for today. Each row MUST link to an existing CAO test/demo at the pinned
commit, or be scoped down to what is provable. Do not let the table become
aspirational marketing — that discipline is what has earned the credibility so
far.

---

## 3. PR lede (maintainer-facing — adapt, don't paste blindly)

**TL;DR (top line):**

> The first AG-UI source that drives **real CLI coding-agent processes** — and the
> first to let you **approve or deny a live permission prompt from the browser**
> through AG-UI's own interrupt lifecycle.

**Opening paragraph:**

> Every AG-UI integration today wraps a single framework and assumes an
> addressable HTTP agent already exists. CAO fills the empty axis no one else
> does: it runs each coding agent (Kiro CLI, Claude Code, Codex, …) as a **real
> OS process** in an isolated tmux session, coordinates them supervisor→worker
> over MCP, and projects that live fleet through AG-UI — so a stock
> `@ag-ui/client` renders it with **zero custom adapter code**. The flagship is
> something an API wrapper structurally cannot do: when a CLI agent hits a real
> permission prompt, CAO closes the run with `RUN_FINISHED
> outcome={type:"interrupt"}` and resolves it idempotently from a `resume[]` —
> you **approve or deny a live agent's actual prompt from the browser**, over the
> standard interrupt lifecycle. The bet underneath it: normalizing over N
> heterogeneous runtimes *without* coupling to any provider's low-level
> implementation is the scalable way to build multi-agent UIs — add a provider by
> implementing one base interface, and it appears in every construct and every
> AG-UI client for free. That makes CAO less "another integration" and more a
> **real-process reference implementation and production testbed** for the parts
> of the AG-UI roadmap that are hardest to validate (sub-agents & composition,
> interrupts/HITL, agent steering, tool-output streaming, read-write shared
> state, declarative generative UI, background agents — mapped row-by-row below).
> And it's proven the way we build everything: **keyless and shift-left** — the
> whole feature set is exercised by a fail-closed contract suite that goes red the
> instant the wire drifts (the `mock_cli` fleet needs no API keys, so the entire
> e2e matrix runs secret-free) — and **dogfooded**: the real-provider evidence is
> CAO's own audit fleet visualizing itself through this exact surface.

**Pull-quote under the interrupt demo GIF:**

> No mock, no recording: a real (keyless) CLI permission prompt, approved from the
> browser, resolved exactly-once against the waiting process — metadata only,
> message bodies never on the wire.

**Lede guardrails:** the paragraph says "mapped row-by-row below," so it must be
followed by the roadmap table with each row linked to a verifiable artifact. The
"audit fleet visualizing itself" sentence depends on shipping the
`ag-ui-meta-dogfood` evidence via canonical `awslabs/…` URLs — wire that in
before using the line.



---

## 4. Related PRs (fork: plauzy/ag-ui)

| PR | Branch | Scope |
|---|---|---|
| [#4](https://github.com/plauzy/ag-ui/pull/4) | `spec/cao-agui-integration` | The spec plan (requirements / design / tasks) |
| [#5](https://github.com/plauzy/ag-ui/pull/5) | `feat/cao-agui-integration` | The implementation (TS thin client + keyless server + Dojo wiring + tests) |
| [#6](https://github.com/plauzy/ag-ui/pull/6) | `spec/cao-agui-handoff` | This handoff (differentiators + worker prompt + PR lede) |

> Cross-links live only in these `.kiro/` planning docs. The upstream-bound
> integration code in #5 deliberately carries **no fork PR numbers** — it must be
> clean for `ag-ui-protocol/ag-ui`.

---

## 5. Executing this plan with a CAO fleet (dogfood the orchestrator)

The highest-leverage move is to build the remaining work **with a CAO fleet** —
so finishing the integration *is* the flagship demo: the fleet, observed through
the very AG-UI surface it ships (the `ag-ui-meta-dogfood` "audit fleet
visualizes itself" loop).

**Topology (heterogeneous on purpose — proves differentiator #2):**
- **Supervisor** (`kiro_cli`) — owns `.kiro/specs/*`, decomposes `tasks.md`,
  delegates, gates.
- **Worker A** (`claude_code`) — TS client + vitest.
- **Worker B** (`codex`) — Python example server + pytest contract suite.
- **Worker C** (`kiro_cli`) — Dojo wiring + Playwright `caoTests` + `dojo-e2e.yml`.
- **Reviewer** (any provider) — runs the gates, reviews diffs, blocks on red.

**Wiring — all CAO built-ins:**
- Supervisor spawns each worker as a real tmux process and delegates over MCP
  (`send_message` / handoff); uses inbox delivery to steer running terminals
  mid-run.
- Observe the entire run live on `GET /agui/v1/stream`, folded by
  `SupervisorDashboardStream` + `MultiAgentSessionTimeline`.
- Worker permission prompts surface as AG-UI interrupts via
  `AgentHandoffWithApproval` → supervisor/human answers with `resume[]`. The
  build **exercises differentiator #3 on itself**.
- Progress/diffs via the allow-listed `emit_ui` components.

**Shift-left gate (non-negotiable):** the supervisor does NOT accept a task until
its fail-closed proof is green — a red gate is a handoff *back* to the worker,
never a merge:
- Worker A: `pnpm build && pnpm test && pnpm test:exports`
- Worker B: `uv run --extra test pytest` (7/7)
- Worker C: local Dojo `caoTests` green, incl. the interrupt **approve AND deny**

**Dogfood capture:** run it through `examples/ag-ui/ag-ui-meta-dogfood` +
`ag-ui-construct-demos` so a PASS emits the GIFs the upstream PR embeds (canonical
`awslabs/…` URLs). The recording of the fleet *finishing this integration* is the
PR's real-provider evidence.

**Cross-provider proof:** assign the SAME feature (e.g. `shared_state`) to ≥3
providers and assert uniform rendering (`CrossProviderStateSync`) — captured in
the same run.

**One-liner to hand the supervisor:**

```
Read .kiro/specs/cli-agent-orchestrator-integration/{requirements,design,tasks,handoff}.md.
Execute tasks.md via a heterogeneous worker fleet (kiro_cli, claude_code, codex).
Gate every task on its fail-closed test; hand a task back on red, never merge red.
Answer worker permission prompts through the AG-UI interrupt lifecycle (resume[]).
Record the run via ag-ui-meta-dogfood for the PR evidence.
Canonical awslabs URLs only; pin CAO to edf61cad; strictly additive.
```
