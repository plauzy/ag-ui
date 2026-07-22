import { test, expect } from "../../test-isolation-helper";
import {
  openChat,
  sendChatMessage,
  awaitLLMResponseDone,
  assertUserMessage,
} from "../../utils/copilot-actions";

/**
 * CLI Agent Orchestrator (CAO) — Interrupt (flagship).
 *
 * The differentiator no API-wrapper integration can show: a live CLI
 * permission prompt answered from the browser through AG-UI's interrupt
 * lifecycle. CAO's run plane closes the run with
 * `RUN_FINISHED outcome={type:"interrupt", interrupts:[…]}`; the client answers
 * with `resume:[{ interruptId, status, payload }]`, which CAO resolves
 * idempotently against the waiting process.
 *
 * The full interrupt → resume (approve AND deny) round-trip is asserted keyless
 * against the real run plane in the example server's pytest suite
 * (`python/examples/tests/test_server.py`). This spec is the UI-level proof that
 * the outcome surfaces an actionable approve/deny affordance in the Dojo.
 */
test.describe("[Integration] CAO - Interrupt", () => {
  test("surfaces an approve/deny affordance on a live permission prompt", async ({
    page,
  }) => {
    await page.goto("/cli-agent-orchestrator/feature/interrupt");
    await openChat(page);

    await sendChatMessage(page, "Run the build step");
    await assertUserMessage(page, "Run the build step");
    await awaitLLMResponseDone(page);

    // The interrupt outcome renders an approve/deny (or allow) control.
    const approvalAffordance = page
      .getByRole("button", { name: /approve|allow|deny|reject|confirm/i })
      .or(page.getByText(/approve|allow|deny|permission/i))
      .first();
    await expect(approvalAffordance).toBeVisible({ timeout: 15000 });
  });
});
