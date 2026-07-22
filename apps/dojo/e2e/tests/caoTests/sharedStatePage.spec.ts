import { test, expect } from "../../test-isolation-helper";
import {
  openChat,
  sendChatMessage,
  awaitLLMResponseDone,
  assertUserMessage,
} from "../../utils/copilot-actions";
import { CopilotSelectors } from "../../utils/copilot-selectors";

/**
 * CLI Agent Orchestrator (CAO) — Shared State.
 *
 * The run plane emits a fleet `STATE_SNAPSHOT` on open and an RFC-6902
 * `STATE_DELTA` (an `add` on `/last_file_mod`) as the fleet changes — metadata
 * only, no file bodies on the wire. This UI smoke drives a run and asserts it
 * completes; the snapshot/delta frames are asserted keyless in the server's
 * pytest suite.
 */
test.describe("[Integration] CAO - Shared State", () => {
  test("streams fleet state and completes a run", async ({ page }) => {
    await page.goto("/cli-agent-orchestrator/feature/shared_state");
    await openChat(page);

    await sendChatMessage(page, "Show fleet state");
    await assertUserMessage(page, "Show fleet state");

    await awaitLLMResponseDone(page);
    await expect(CopilotSelectors.messageList(page)).toBeVisible();
  });
});
