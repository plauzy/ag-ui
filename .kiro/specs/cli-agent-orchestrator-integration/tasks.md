# Tasks — CLI Agent Orchestrator (CAO) AG-UI Integration

> Ground truth: CAO @ `edf61cad65a8183d37466f2d112d19a365cfca5c`
> (`awslabs/cli-agent-orchestrator`, PRs #485/#458). Mirror
> `integrations/aws-strands/`. Every task cites the requirement(s) it satisfies.
> **Verification habit (from prior learnings):** before committing, `grep` the
> incorporated/authored files for a known marker from the pinned commit and
> confirm no fork/non-canonical URLs leaked.

## 0. Reconcile with the existing open PR
- [ ] 0.1 Diff this plan against the file list of `ag-ui-protocol/ag-ui#2216`;
  note every file that PR touches so none are silently dropped (enumerate the
  full PR file tree, not just the TS client). (R1, R4, R7)
- [ ] 0.2 Confirm the CAO surface exists at the pinned commit: `POST /agui/v1/run`,
  `POST /agui/v1/interrupts/{id}/resume`, `GET /agui/v1/stream`, `emit_ui`, the
  `[agui]` extra range `ag-ui-protocol>=0.1.19,<0.2.0`. Stop & flag if any is
  absent at that commit. (Determinism rule)

## 1. Scaffold the integration directory (R1)
- [ ] 1.1 Create `integrations/cli-agent-orchestrator/{typescript,python}` +
  `ARCHITECTURE.md`, copying structure from `integrations/aws-strands/`.
- [ ] 1.2 `ARCHITECTURE.md`: document the L1/L2/L3 construct model and the
  "real processes **and** protocol" positioning; link the pinned CAO commit +
  `docs/agui.md`. (R1.1, differentiators)

## 2. TypeScript thin client (R2, R1.2, R1.3)
- [ ] 2.1 `typescript/src/index.ts`: export
  `class CliAgentOrchestratorAgent extends HttpAgent {}` — no extra wire code. (R2.1)
- [ ] 2.2 `typescript/package.json`: name `@ag-ui/cli-agent-orchestrator`;
  scripts `build`(tsdown)/`test`(vitest)/`test:exports`(publint --strict && attw --pack)/`typecheck`;
  peerDeps `@ag-ui/client|core|encoder`; MIT; `publishConfig.access=public`. (R1.2, R1.3)
- [ ] 2.3 Add `tsconfig.json` + `tsdown.config.ts` mirroring aws-strands.
- [ ] 2.4 `typescript/README.md`: usage; canonical CAO repo links only. (R7.1)

## 3. Keyless example server (R3)
- [ ] 3.1 `python/examples/pyproject.toml`: pin `cli-agent-orchestrator[agui]`
  (matching the pinned commit's release) + `uvicorn`; **no** dependency on a CAO
  source checkout. (R3.5)
- [ ] 3.2 `server/agentic_chat.py` — mock_cli run over `POST /agui/v1/run`. (R3.1, R3.2)
- [ ] 3.3 `server/shared_state.py` — snapshot + RFC-6902 delta feature. (R3.2)
- [ ] 3.4 `server/human_in_the_loop.py` — approval affordance from fleet activity. (R3.2)
- [ ] 3.5 `server/interrupt.py` (**flagship**) — real mock permission prompt →
  `RUN_FINISHED outcome={type:"interrupt"}` → `resume[]` round-trip via the CAO
  endpoints (do not reimplement the encoder/registry). (R3.3)
- [ ] 3.6 App bootstrap: port **8024**, `/health`, CORS; sets `CAO_AGUI_ENABLED=1`. (R3.4)
- [ ] 3.7 `python/README.md` + `examples/README.md`: run steps; canonical links. (R7.1)

## 4. Dojo wiring (R4)
- [ ] 4.1 `apps/dojo/src/menu.ts`: add `cli-agent-orchestrator` with the four
  features. (R4.1)
- [ ] 4.2 `apps/dojo/src/env.ts`: add `caoUrl` (default `http://localhost:8024`). (R4.2)
- [ ] 4.3 `apps/dojo/src/agents.ts`: import + register a `cli-agent-orchestrator`
  factory (`mapAgents` over the four features against `caoUrl`). (R4.2)
- [ ] 4.4 `apps/dojo/package.json`: add `@ag-ui/cli-agent-orchestrator: workspace:*`;
  refresh `pnpm-lock.yaml`. (R4.3)
- [ ] 4.5 `apps/dojo/src/files.json` + `scripts/generate-content-json.ts`: map the
  four Python feature files into the Dojo code viewer. (R4.3)
- [ ] 4.6 `scripts/prep-dojo-everything.js` + `run-dojo-everything.js`: prep/launch
  the CAO example server on 8024 (additive). (R4.3, R8.1)

## 5. Shift-left tests (R5)
- [ ] 5.1 `typescript/src/__tests__/cli-agent-orchestrator-agent.test.ts`:
  assert `HttpAgent` subclass + constructs with `url`. (R5.1)
- [ ] 5.2 `typescript/src/__tests__/docs-canonical-links.test.ts`: fail on any
  non-canonical CAO URL in shipped Markdown. (R5.1, R7.1)
- [ ] 5.3 `apps/dojo/e2e/tests/caoTests/agenticChatPage.spec.ts` — assert a
  rendered assistant turn. (R5.2)
- [ ] 5.4 `.../sharedStatePage.spec.ts` — assert state renders/updates. (R5.2)
- [ ] 5.5 `.../humanInTheLoopPage.spec.ts` — assert the HITL affordance. (R5.2)
- [ ] 5.6 `.../interruptPage.spec.ts` — assert the **approve and deny**
  round-trip completes (the flagship differentiator). (R5.2)
- [ ] 5.7 `.github/workflows/dojo-e2e.yml`: add a keyless `cli-agent-orchestrator`
  matrix entry (boot server + run the four specs, no secrets). (R5.3)

## 6. Dogfooding evidence (R6)
- [ ] 6.1 In the PR body, embed CAO's `ag-ui-meta-dogfood` evidence
  (supervisor→developer→reviewer, `kiro_cli`/`claude_code`/`codex`, live
  `GET /agui/v1/stream`, privacy boundary intact) via canonical raw URLs. (R6.1)
- [ ] 6.2 Reference the `ag-ui-construct-demos` PASS-gated GIFs (handoff-approval,
  supervisor-dashboard, session-timeline, cross-provider-sync, stock client). (R5.4, R6.1)
- [ ] 6.3 Where the environment permits, execute tasks 1–5 via a CAO fleet and
  note it in the PR ("this integration was built by the orchestrator it
  integrates"). (R6.2)

## 7. Docs & governance (R7)
- [ ] 7.1 `docs/integrations.mdx`: add CAO with the one-line differentiator. (R7.1)
- [ ] 7.2 `docs/introduction.mdx`: add CAO to the integration listing. (R7.1)
- [ ] 7.3 `.github/CODEOWNERS`: add the integration dir owner. (R7.2)
- [ ] 7.4 `.github/config-allowlist.txt`: allow the new config paths. (R7.2)

## 8. Verify additivity & finalize (R8)
- [ ] 8.1 Run existing Dojo build + a representative other integration's e2e to
  prove no regression with the CAO server absent. (R8.1, R8.2)
- [ ] 8.2 Full local gate: TS `build`+`test`+`test:exports`+`typecheck`; the four
  e2e specs; `docs-canonical-links` test. All green.
- [ ] 8.3 Marker check: `grep` authored files for canonical `awslabs/cli-agent-orchestrator`
  URLs; confirm zero fork/non-canonical URLs. (Prior-learnings verification habit)
- [ ] 8.4 Open/refresh the PR against `ag-ui-protocol/ag-ui` with "Fixes #2215",
  the differentiator narrative, and the dogfood evidence; reconcile with #2216.

## Suggested PR split (if maintainers prefer smaller reviews)
1. TS client (`@ag-ui/cli-agent-orchestrator`) + its unit tests.
2. Keyless Python example server.
3. Dojo wiring + four Playwright e2e specs + CI matrix entry.
4. Docs + CODEOWNERS + config-allowlist + PR narrative/evidence.

## Definition of done
R1–R8 satisfied; four e2e specs green in CI without secrets; CAO renders in the
Dojo with a working interrupt round-trip; PR carries the differentiator +
dogfood evidence and closes #2215.
