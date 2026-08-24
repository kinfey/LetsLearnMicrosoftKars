# 6. Moving Forge into a Governed Runtime

## The uncomfortable discovery

The policy prototype uses OpenClaw, but Maya's original Forge is a Python
application with custom repository indexing and patch planning. Rewriting it
would delay the project.
Running the old container unchanged would preserve its direct credential and
network assumptions.

The team chooses a third path: keep the application logic, replace the
authority model.

## Choose an adapter intentionally

KARS includes adapters for OpenClaw, Hermes, OpenAI Agents, Microsoft Agent
Framework Python, LangGraph Python and TypeScript, Anthropic, Pydantic-AI, and
bring-your-own (BYO) images.

The team compares needs:

| Application situation | Reasonable starting point |
| --- | --- |
| Exploring broad mesh/handoff support | OpenClaw or Hermes |
| Existing OpenAI Agents code | OpenAI Agents adapter |
| Existing graph workflow | LangGraph adapter |
| Custom process and dependencies | BYO |

An enum value in a schema is not proof of full runtime support. They verify the
adapter in the release-specific runtime matrix and maturity documentation.

## Inventory the old container

Before editing code, Maya documents the existing assumptions:

```text
AZURE_OPENAI_API_KEY -> read by Forge
AZURE_OPENAI_ENDPOINT -> called directly
GITHUB_TOKEN -> passed to repository and pull-request tools
HTTPS_PROXY -> unrestricted company proxy
process user -> root
```

Every line conflicts with the intended sandbox contract.

## Refactor the authority boundary

The BYO image must:

- run as UID 1000;
- send controlled external requests through the router at
  `127.0.0.1:8443`;
- contain no Azure or model-provider credential;
- follow the documented sandbox environment contract;
- write only to permitted runtime locations.

Maya changes model and tool endpoints from hard-coded provider URLs to
configuration. She removes credential acquisition from the Agent. Tool
authentication moves into the KARS/MCP platform configuration.

The application still decides *which code to inspect and which test to run*.
The platform decides whether that action is authorized.

## Test in layers

The team does not jump from `docker run` to AKS.

### 1. Process test

Run the container as UID 1000. Verify startup, health, and writable paths.

### 2. Credential absence test

Inspect the runtime environment and image history. Forge must not find provider
keys even when prompted to enumerate its environment.

### 3. Router-path test

Send one model request and correlate it with a router audit event. If the
request succeeds with the router unavailable, Forge still has an unintended
external path.

### 4. Negative network test

Attempt to reach an unrelated public host. Direct access must fail. The team
does not "fix" this by restoring a general proxy.

### 5. Policy test

Exercise allowed code reads and tests, an unknown tool, rate exhaustion,
token-budget exhaustion, and MCP failure.

## Supply-chain decisions

The team scans the image and pins it by digest for promotion. Published KARS
images include signatures and supply-chain metadata, but automatic rejection
of unsigned BYO images is not yet a complete KARS capability. The cluster must
enforce the organization's image admission policy separately.

They record:

- source revision;
- build workflow identity;
- image digest;
- vulnerability scan result;
- base image;
- KARS version and runtime adapter;
- policy bundle digest.

## A bug that proves the design

During testing, Forge sees a bootstrap command in the repository and tries to
download an unsigned build tool from an unapproved package host. The download
fails under enforced egress.

Maya initially calls this a regression. Lina calls it a newly discovered
capability.

They decide builds must use the pinned toolchain in the approved build image,
so they remove the bootstrap behavior from Forge. The security control forced
a supply-chain decision that had previously been hidden inside repository
instructions.

## Migration checklist

1. Identify every credential and external endpoint.
2. Match the framework to a supported adapter or BYO.
3. Make endpoints configurable.
4. Remove application-owned external credentials.
5. Run as UID 1000.
6. Route controlled calls through `127.0.0.1:8443`.
7. Test explicit failures and denied paths.
8. Scan and pin the image.
9. Record the runtime and policy versions.

## Chapter outcome

Forge still contains Contoso's indexing and patch-planning logic, but it no longer
defines its own authority. The migration changed infrastructure assumptions,
not the business purpose.

## Official references

- [Runtime adapters](https://github.com/Azure/kars/blob/main/docs/runtimes.md)
- [Examples](https://github.com/Azure/kars/tree/main/examples)
- [BYO quickstart](https://github.com/Azure/kars/tree/main/examples/byo-quickstart)
