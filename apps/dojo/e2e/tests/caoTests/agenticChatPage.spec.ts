import { test, expect } from "../../test-isolation-helper";
import {
  openChat,
  sendChatMessage,
  awaitLLMResponseDone,
  assertUserMessage,
} from "../../utils/copilot-actions";
import { CopilotSelectors } from "../../utils/copilot-selectors";

/**
 * CLI Agent Orchestrator (CAO) — Agentic Chat.
 *
 * CAO's keyless `mock_cli` fleet emits a real orchestration lifecycle
 * (`RUN_STARTED → STATE_SNAPSHOT → STEP_* → RUN_FINISHED`) rather than an LLM
 * chat reply — so this UI smoke asserts the message round-trips and the run
 * completes cleanly. The precise wire contract is asserted keyless in the
 * example server's pytest suite (`python/examples/tests/test_server.py`).
 */
test.describe("[Integration] CAO - Agentic Chat", () => {
  test("sends a message and completes a run over the mock_cli fleet", async ({
    page,
  }) => {
    await page.goto("/cli-agent-orchestrator/feature/agentic_chat");
    await openChat(page);

    await sendChatMessage(page, "Kick off a run");
    await assertUserMessage(page, "Kick off a run");

    // The run reaches RUN_FINISHED and the UI returns to idle.
    await awaitLLMResponseDone(page);
    await expect(CopilotSelectors.messageList(page)).toBeVisible();
  });
});
