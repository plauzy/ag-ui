import { test, expect } from "../../test-isolation-helper";
import {
  openChat,
  sendChatMessage,
  awaitLLMResponseDone,
  assertUserMessage,
} from "../../utils/copilot-actions";
import { CopilotSelectors } from "../../utils/copilot-selectors";

/**
 * CLI Agent Orchestrator (CAO) — Human in the Loop.
 *
 * A fleet worker authors an allow-listed `approval_card` generative-UI intent
 * (approve/deny/edit affordance), projected to a stock `CUSTOM`
 * (`cao.generative_ui`) frame. Off-list components are refused by CAO's
 * allow-list. This UI smoke drives the run and asserts completion; the
 * approval_card frame is asserted keyless in the server's pytest suite.
 */
test.describe("[Integration] CAO - Human in the Loop", () => {
  test("surfaces an approval affordance and completes", async ({ page }) => {
    await page.goto("/cli-agent-orchestrator/feature/human_in_the_loop");
    await openChat(page);

    await sendChatMessage(page, "Request approval for the build step");
    await assertUserMessage(page, "Request approval for the build step");

    await awaitLLMResponseDone(page);
    await expect(CopilotSelectors.messageList(page)).toBeVisible();
  });
});
