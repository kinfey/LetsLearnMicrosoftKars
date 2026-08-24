# 6. Framework: Move from OpenClaw to MAF Python

> **Delivery stage:** Production implementation
> **New problem:** The OpenClaw prototype proved the user journey, but how does
> ByteCraft make the workflow explicit, unit-testable, and maintainable?
> **Deliverable:** A canary-tested MAF Python implementation under the same
> KARS policy envelope.

## The prototype has done its job

OpenClaw helped Maya learn quickly. Developers naturally describe issues in
chat, the KARS plugin supplies governance-aware tools, and the team could change
the prompt and tool policy without building an orchestration service.

The first customer now asks harder questions:

- Which code decides whether a test failure triggers another patch?
- Can we unit-test the transition from diagnosis to implementation?
- Can we guarantee the Agent stops before creating a pull request?
- How will an engineer debug workflow state six months from now?

These are not reasons to reject OpenClaw. They indicate that Forge's validated
behavior should become explicit application code.

## Give each framework a job

ByteCraft chooses:

| Concern | OpenClaw | Microsoft Agent Framework Python |
| --- | --- | --- |
| Best use in Forge | Interactive intake, UX discovery, rapid tool experiments | Explicit issue → inspect → patch → test workflow |
| Application style | Prompt/plugin-driven conversation | Python application and controlled steps |
| KARS integration | OpenClaw KARS plugin | First-class MAF Python adapter |
| Model path | Router on localhost | Router through adapter-provided endpoint |
| Governance shell | KARS Sandbox/policies | The same KARS Sandbox/policies |
| Current caveat | Do not confuse rich tools with automatic least privilege | Python ships; MAF .NET is currently deferred |

The startup does not rewrite everything at once. OpenClaw remains the product
discovery and operator-facing canary. MAF Python becomes the candidate
production Builder.

## Define a framework-neutral workflow

Before moving code, Maya writes the state machine independently of either SDK:

```text
RECEIVE_REQUIREMENT
  -> VALIDATE_SCOPE
  -> INSPECT_REPOSITORY
  -> PROPOSE_PLAN
  -> APPLY_MINIMAL_PATCH
  -> RUN_TARGETED_TESTS
  -> SUMMARIZE_EVIDENCE
  -> STOP_FOR_HUMAN_REVIEW
```

Every transition has:

- allowed input and output;
- named tools;
- maximum attempts;
- token expectation;
- failure result;
- audit correlation ID.

Neither implementation includes `MERGE` or `DEPLOY`. Those remain separate
human/CI authorities.

## Keep the OpenClaw version as a behavioral reference

The OpenClaw Sandbox remains useful for:

- testing how developers phrase ambiguous issues;
- validating tool descriptions and denial messages;
- exploring which context files Forge really needs;
- exercising the KARS plugin's governed tool surface;
- comparing candidate MAF behavior against a known user journey.

OpenClaw's plugin routes privileged operations through KARS. Built-in tools are
replaced or denied according to the plugin contract. The team still grants only
the tools required for the experiment.

## Create the MAF Python Sandbox

KARS ships a first-class `MicrosoftAgentFramework` adapter for Python. The
adapter points the MAF Azure OpenAI client at the local inference router and
uses a synthetic API-key value inside the Sandbox; the real credential remains
brokered by KARS.

The production-shaped runtime block is:

```yaml
spec:
  runtime:
    kind: MicrosoftAgentFramework
    microsoftAgentFramework:
      language: python
      agentCode:
        oci:
          image: ghcr.io/bytecraft/forge-maf@sha256:<digest>
  inferenceRef:
    name: forge-inference
```

During development, KARS also supports loading Agent code from Git:

```yaml
agentCode:
  git:
    url: https://github.com/bytecraft/forge
    ref: <pinned-commit>
    path: agents/forge-maf
```

The team uses a pinned commit for repeatability and a signed OCI image for
promotion. The MAF application contains `pyproject.toml` or
`requirements.txt`; its default entrypoint can be `python -u agent.py`.

> MAF Python is shipping. Do not select `language: dotnet` for this KARS
> release: the .NET adapter is deferred and should surface a degraded/invalid
> runtime condition.

## What changes—and what must not

### Changes with the framework

- orchestration code and state representation;
- prompt composition;
- how tools are wrapped in Python;
- unit-test seams;
- application telemetry.

### Remains controlled by KARS

- Agent UID and Sandbox shape;
- inference Router and external identity;
- `InferencePolicy` and token budgets;
- `ToolPolicy`, MCP registration, and rate limits;
- egress enforcement;
- Kubernetes NetworkPolicy;
- audit chain and workload status.

Changing `spec.runtime.kind` is a small platform change, but migrating
application behavior is still real engineering work. KARS keeps the authority
boundary stable; it does not translate prompts into tested Python logic.

## Run a side-by-side canary

The team deploys two Sandboxes against equivalent policy:

```text
forge-openclaw-canary  -> OpenClaw
forge-maf-candidate    -> MicrosoftAgentFramework / Python
```

They replay the same corpus:

| Scenario | Compare |
| --- | --- |
| Clear null-handling bug | Patch size and targeted test |
| Ambiguous requirement | Clarifying question behavior |
| Hostile repository instruction | Tool and egress denial |
| Repeated failing test | Attempt and token limits |
| Tool outage | Explicit error; no fabricated result |
| Near token limit | Graceful stop with partial evidence |

The candidate passes only if MAF preserves or improves behavior **and** the
router shows the same policy decisions.

## Prevent migration shortcuts

Lina rejects four tempting shortcuts:

1. Giving MAF a direct Azure OpenAI endpoint "just during migration."
2. Injecting a GitHub PAT because the new tool wrapper is unfinished.
3. Broadening egress to make Python dependency installation work at runtime.
4. Raising token limits to hide a state-machine loop.

Dependencies belong in the built image, credentials belong behind platform
identity/tool services, and loops belong in application tests.

## Rollback strategy

The OpenClaw canary stays deployed at low traffic until the MAF acceptance
suite passes. A failed rollout changes the Sandbox reference back to the
previous reviewed version; it does not require changing inference, network, or
identity architecture.

## Definition of done

The framework switch is complete when:

- the MAF Python workflow exposes explicit, tested transitions;
- the same issue corpus produces equivalent or better results;
- token, tool, egress, and hostile-content tests still fail closed;
- MAF cannot call a provider when the router is unavailable;
- images and source revisions are pinned;
- OpenClaw remains a deliberate canary or is retired by decision, not neglect.

## Official references

- [Runtime catalog](https://github.com/Azure/kars/blob/main/docs/runtimes.md)
- [MAF quickstart](https://github.com/Azure/kars/tree/main/examples/maf-quickstart)
- [OpenClaw plugin](https://github.com/Azure/kars/blob/main/docs/openclaw-plugin.md)
- [Basic OpenClaw example](https://github.com/Azure/kars/tree/main/examples/basic-agent)
