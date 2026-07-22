import { describe, it, expect } from "vitest";
import { HttpAgent } from "@ag-ui/client";
import { CliAgentOrchestratorAgent } from "../index";

describe("CliAgentOrchestratorAgent", () => {
  it("is a thin HttpAgent subclass (zero extra wire code)", () => {
    const agent = new CliAgentOrchestratorAgent({
      url: "http://localhost:8024/agui/v1/run",
    });
    expect(agent).toBeInstanceOf(HttpAgent);
    expect(agent).toBeInstanceOf(CliAgentOrchestratorAgent);
  });

  it("constructs against a CAO run-plane URL and preserves it", () => {
    const url = "http://localhost:8024/agentic-chat/";
    const agent = new CliAgentOrchestratorAgent({ url });
    // HttpAgent stores the endpoint on `url`.
    expect((agent as unknown as { url: string }).url).toBe(url);
  });

  it("adds no CAO-specific surface beyond HttpAgent", () => {
    // Contract guard: if this class ever grows its own protocol/transport
    // methods, that is a signal the CAO run-plane contract was misread. The
    // thin-projection invariant is that own instance keys match a bare
    // HttpAgent constructed with the same config.
    const cfg = { url: "http://localhost:8024/agui/v1/run" };
    const thin = new CliAgentOrchestratorAgent(cfg);
    const base = new HttpAgent(cfg);
    expect(Object.keys(thin as object).sort()).toEqual(
      Object.keys(base as object).sort(),
    );
  });
});
