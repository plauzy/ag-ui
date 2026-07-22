import { describe, it, expect } from "vitest";
import * as fs from "fs";
import * as path from "path";

/**
 * Guard: shipped Markdown for this integration must reference ONLY the
 * canonical upstream CAO repository (`github.com/awslabs/cli-agent-orchestrator`).
 *
 * The reference implementation was iterated on a fork; this test fails closed
 * if any fork/non-canonical CAO GitHub URL (e.g. a `plauzy/…` fork or a
 * `/blob/feat/…` branch link) leaks into published docs, so downstream readers
 * are never pointed at a non-authoritative source.
 */

const CANONICAL_OWNER = "awslabs";
const REPO = "cli-agent-orchestrator";

// Root of the integration directory: src/__tests__ -> src -> typescript -> <root>.
const INTEGRATION_ROOT = path.resolve(__dirname, "..", "..", "..");

function collectMarkdown(dir: string, acc: string[] = []): string[] {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name === "dist") continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      collectMarkdown(full, acc);
    } else if (/\.(md|mdx)$/i.test(entry.name)) {
      acc.push(full);
    }
  }
  return acc;
}

// Any github.com URL that mentions the CAO repo but not under the canonical owner.
const CAO_GITHUB_URL = new RegExp(
  `https?://(?:www\\.)?github\\.com/([\\w.-]+)/${REPO}(?:[/#?][^\\s)"'\\]]*)?`,
  "gi",
);
// raw.githubusercontent.com/<owner>/cli-agent-orchestrator/...
const CAO_RAW_URL = new RegExp(
  `https?://raw\\.githubusercontent\\.com/([\\w.-]+)/${REPO}/`,
  "gi",
);

describe("docs canonical CAO links", () => {
  const files = collectMarkdown(INTEGRATION_ROOT);

  it("finds shipped Markdown to scan", () => {
    expect(files.length).toBeGreaterThan(0);
  });

  it("references only the canonical awslabs CAO repo", () => {
    const violations: string[] = [];
    for (const file of files) {
      const text = fs.readFileSync(file, "utf8");
      for (const re of [CAO_GITHUB_URL, CAO_RAW_URL]) {
        for (const m of text.matchAll(re)) {
          const owner = m[1];
          if (owner !== CANONICAL_OWNER) {
            violations.push(
              `${path.relative(INTEGRATION_ROOT, file)}: non-canonical owner "${owner}" in ${m[0]}`,
            );
          }
        }
      }
    }
    expect(violations, violations.join("\n")).toEqual([]);
  });
});
