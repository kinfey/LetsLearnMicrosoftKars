# 5. Runtimes and Bring Your Own Agent

## Runtime adapters

KARS supports adapters for OpenClaw, Hermes, OpenAI Agents, Microsoft Agent
Framework Python, LangGraph Python and TypeScript, Anthropic, Pydantic-AI, and
bring-your-own (BYO) images.

Choose by capability rather than name:

| Need | Starting point |
| --- | --- |
| Broad KARS mesh/handoff experience | OpenClaw or Hermes |
| Existing OpenAI Agents application | OpenAI Agents adapter |
| Graph workflow | LangGraph adapter |
| Existing custom container | BYO |

Some runtime names may exist in schemas before their adapters are complete.
The current runtime matrix is authoritative.

## Adapter contract

An adapter translates framework-specific model and tool calls into the KARS
router contract. This keeps provider credentials and external policy outside
the application process.

Use an upstream quickstart before creating a custom image:

- `examples/openai-agents-quickstart`
- `examples/maf-quickstart`
- `examples/hermes-quickstart`
- `examples/byo-quickstart`

## BYO requirements

A custom image must:

- run as UID 1000;
- send external requests through the router at `127.0.0.1:8443`;
- avoid embedded Azure or provider credentials;
- follow the documented sandbox environment contract;
- write ephemeral data only where the runtime permits.

Treat failure to reach the public internet directly as expected behavior, not a
network bug to bypass.

## Integration workflow

1. Make model and tool endpoints configurable.
2. Remove credential acquisition from the agent.
3. Run the process as a non-root user with UID 1000.
4. Build and scan the image.
5. Deploy it with the BYO runtime.
6. Verify inference through router audit logs.
7. Exercise denied egress and budget exhaustion.
8. Pin the image by digest for promotion.

Published KARS images are signed and include supply-chain metadata, but
automatic admission rejection of unsigned BYO images is not yet complete.
Enforce image policy separately in production.

## Exercise

Adapt a minimal agent that sends one model request. First run it with direct
provider credentials, then refactor it so the image contains no credential and
uses the router endpoint. Compare the container environment and network path.

## Official references

- [Runtime adapters](https://github.com/Azure/kars/blob/main/docs/runtimes.md)
- [Examples](https://github.com/Azure/kars/tree/main/examples)
- [BYO quickstart](https://github.com/Azure/kars/tree/main/examples/byo-quickstart)
