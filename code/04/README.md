# KARS policy and tools lab

[English](README.md) | [简体中文](README.zh.md)

This lab turns Chapter 5 into executable governance checks against the Forge
environment from [`code/01`](../01/), using the boundary and evidence patterns
from [`code/02`](../02/) and [`code/03`](../03/). It follows the upstream
[KARS MCP guide](https://github.com/Azure/kars/blob/main/docs/mcp.md),
[CRD reference](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md),
and [security model](https://github.com/Azure/kars/blob/main/docs/security.md).

## Three independent tool boundaries

| Layer | Responsibility |
|-------|----------------|
| `McpServer` | Coarse server registration, exact `allowedTools`, and allowed Sandbox selector |
| `ToolPolicy` | AGT capabilities, approval mode, rate limit, and router-loaded policy digest |
| Workspace MCP implementation | Path normalization, patch scope, test ID allow-list, fixed argv, and diff-size limits |

The layers are intentionally redundant. A tool being advertised is not proof
that a caller is authorized, and a prompt instruction is not a substitute for
input validation.

## What the lab proves

- `forge-workspace-tools` is `Ready=True/RouterEnforcing`.
- The ToolPolicy status digest matches the compiled ConfigMap digest.
- The coordinator receives all seven `tool:workspace_*` capabilities.
- Specialist policy contains inference and mesh capabilities but no workspace
  tool capability.
- `McpServer/forge-workspace` selects only the Forge label.
- Runtime `tools/list` exactly matches the seven `allowedTools`.
- No shell, upload, arbitrary network, or environment-reading tool is exposed.
- Path traversal, CI modification, unknown tools, and unapproved tests fail.
- The approved minimal patch and `format-user` test succeed.
- A request for 20,001 tokens exceeds the 20,000 per-request budget and returns
  HTTP 429 without consuming a successful model call.
- A short MCP outage produces an empty Service endpoint set and the Deployment
  returns to Ready afterward.

Rate-limit configuration is verified through the compiled profile and
`RouterEnforcing` digest echo. The lab deliberately does not flood the live
router merely to exhaust its token bucket.

## Microsoft package sources

The lab applies and verifies:

- npm: `https://packagefeedproxy.microsoft.io/npm/`
- PyPI: `https://packagefeedproxy.microsoft.io/pypi/simple/`
- NuGet: `https://packagefeedproxy.microsoft.io/nuget/v3/index.json`

Upstream source files are restored when the lab exits.

## Run

Keep the validated `code/01` Forge environment running:

```bash
cd code/04
make test
```

The command temporarily forwards the internal MCP Service to
`127.0.0.1:18931`, runs JSON-RPC requests, resets the disposable fixture before
and after patch testing, and closes the port-forward through a shell trap.

The outage test scales only `forge-workspace-mcp` to zero, verifies that its
Service has no ready endpoint, restores one replica, and waits for rollout
completion.

## Evidence

Each run stores evidence under:

```text
.evidence/<UTC timestamp>/
├── transcript.log
├── inference-policy.json
├── coordinator-tool-policy.json
├── specialist-tool-policy.json
├── mcp-server.json
├── compiled-tool-profile.json
├── compiled-inference-profile.json
├── mcp-tools-list.json
├── mcp-runtime-tools.txt
├── mcp-declared-tools.txt
├── denied-traversal.json
├── denied-unknown-tool.json
├── denied-test.json
├── denied-ci-patch.json
├── allowed-patch.json
├── allowed-test.json
├── allowed-diff.json
├── budget-denial.json
├── controller.log
└── router.log
```

The evidence directory is ignored by Git.

## Individual commands

```bash
make inspect
make clean
```

`make clean` restores one ready workspace MCP replica and preserves local
evidence.

## Platform support

The validated environment is macOS arm64. Platform detection is inherited from
`code/01`, including macOS amd64, Linux amd64, and Windows amd64 through Ubuntu
WSL2.
