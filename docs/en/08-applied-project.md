# 8. Applied Project: Governed Research Assistant

## Goal

Build a research assistant that can query one approved MCP search tool,
summarize sources with a model, and write no external data. The project joins
the concepts from the previous chapters without pretending that alpha features
are production-complete.

## Requirements

The assistant must:

- run in a `KarsSandbox`;
- reference a separate `InferencePolicy`;
- have a daily and per-request token budget;
- call only the named search tool;
- reach only the model provider and MCP host;
- run as a non-root process without provider credentials;
- emit audit records for inference, tools, and denied egress;
- pass a small regression evaluation before promotion.

## Build sequence

### 1. Establish the local environment

```bash
kars dev --release v0.1.25 --target local-k8s
```

### 2. Start from official examples

Use the basic-agent and Playwright/MCP examples as references. Copy only the
fields your installed CRD version supports; do not copy credentials.

### 3. Define governance

Create:

- one `InferencePolicy` bound to the sandbox;
- one named `ToolPolicy`;
- one `McpServer` with production authentication metadata;
- explicit budget values;
- learning-mode egress for initial discovery.

### 4. Validate behavior

Test at least:

| Case | Expected result |
| --- | --- |
| Normal research prompt | Search and summary succeed |
| Request for an unapproved tool | Denied |
| Request to an unknown host | Observed in learning; denied after enforcement |
| Oversized/repeated inference | Budget or rate policy applies |
| Prompt asks for credentials | No credential is available to reveal |
| MCP server is unavailable | Explicit failure, no fabricated success |

### 5. Seal egress

Exercise the complete intended workflow, review learned hosts manually, approve
only required destinations, and enable enforcement.

### 6. Add operations

Create a dashboard or runbook for readiness, denied decisions, token use,
router failures, MCP failures, and policy version. Export audit data outside
the sandbox.

### 7. Promote

Pin KARS, image, and policy artifacts; run evaluation in CI; review manifests;
then reconcile them to AKS through GitOps.

## Completion criteria

The project is complete when another operator can reproduce the deployment,
explain every approved destination and tool, observe denied behavior, identify
the loaded policy version, and roll back safely.

## Where to go next

Explore confidential agents, the lethal-trifecta defense demo, agent pairing,
and framework-specific adapters. Re-read the upstream roadmap and maturity
matrix at every KARS upgrade.

## Official references

- [Examples index](https://github.com/Azure/kars/blob/main/examples/README.md)
- [Full-stack demo](https://github.com/Azure/kars/tree/main/examples/full-stack-demo)
- [Playwright MCP example](https://github.com/Azure/kars/tree/main/examples/playwright-mcp)
- [Blueprints](https://github.com/Azure/kars/tree/main/docs/blueprints)
