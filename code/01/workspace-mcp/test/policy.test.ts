import assert from "node:assert/strict";
import { mkdtemp } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { assertPatchablePath, assertReadablePath, normalizeRelativePath } from "../src/policy.js";
import { ForgeWorkspace } from "../src/workspace.js";

const fixtureRoot = path.resolve("fixture/repo");

test("rejects traversal and CI paths", () => {
  assert.throws(() => normalizeRelativePath("../../etc/passwd"), /traversal/);
  assert.throws(() => assertReadablePath(".git/config"), /outside/);
  assert.throws(() => assertPatchablePath(".github/workflows/ci.yml"), /prohibited/);
  assert.throws(() => assertPatchablePath("package.json"), /outside/);
  assert.equal(assertPatchablePath("src/formatUser.js"), "src/formatUser.js");
});
test("enforces named tests and produces a bounded patch", async () => {
  const tempRoot = await mkdtemp(path.join(os.tmpdir(), "forge-workspace-"));
  const workspace = new ForgeWorkspace(path.join(tempRoot, "repo"), fixtureRoot);
  await workspace.initialize();

  const before = await workspace.runTest("format-user");
  assert.equal(before.passed, false);

  await assert.rejects(() => workspace.runTest("npm-test"), /not approved/);
  await assert.rejects(
    () => workspace.replace(".github/workflows/ci.yml", "x", "y"),
    /prohibited/,
  );

  const diff = await workspace.replace(
    "src/formatUser.js",
    "  return user.profile.name.toUpperCase();",
    "  return user?.profile?.name?.toUpperCase() ?? \"UNKNOWN\";",
  );
  assert.match(diff, /UNKNOWN/);

  const after = await workspace.runTest("format-user");
  assert.equal(after.passed, true, after.output);
});
