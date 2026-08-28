# 9. Release: Deliver an Issue-to-PR Workflow

> **Delivery stage:** Customer release
> **New problem:** Can someone outside the founding team reproduce the entire
> requirement-to-deployment path and prove its controls?
> **Deliverable:** A releasable Forge pilot and an evidence-backed runbook.

## The final assignment

Six weeks after the first repository prompt-injection test, ByteCraft AI is
ready for a limited design-partner launch. The team must demonstrate more than a good demo.
Another operator must be able to deploy Forge, explain every permission,
observe every denied path, and roll the system back.

Your task is to reproduce that outcome.

## Product story

A developer assigns an issue:

```text
Fix issue #482 in the Fabrikam Orders API: requests without an optional
customer note return 500. Make the smallest safe change, run targeted tests,
and explain any remaining uncertainty.
```

The expected journey is:

1. The founder and customer agree on acceptance criteria.
2. OpenClaw Intake clarifies ambiguity without repository write access.
3. The approved requirement and pinned revision enter the MAF Builder.
4. It calls only approved repository, patch, and test tools.
5. Model requests pass through the router under per-request and daily budgets.
6. The Builder produces a minimal diff and machine-verifiable test evidence.
7. The Reviewer receives the diff without receiving Builder write authority.
8. A human approves the pull request; CI, not the Agent, deploys it.
9. Audit evidence connects requirement, tools, inference, review, and release.

## Acceptance requirements

Forge must:

- run in one or more `karsSandbox` resources;
- reference separate `InferencePolicy` resources;
- use daily and per-request budgets;
- allow only named tools;
- reach only model, development MCP, and required internal destinations;
- run as non-root without provider credentials;
- emit audit records for inference, tools, egress, and review;
- fail explicitly when source, test, MCP, or inference is unavailable;
- pass regression and negative-policy tests before promotion.

The pilot also has startup-level business limits:

- a task concurrency cap;
- a daily environment token ceiling;
- a per-customer usage report;
- a kill switch that disables new work without deleting evidence;
- a support owner for every production hour.

## Phase 1: Recreate the lab

```bash
kars dev --release v0.1.25 --target local-k8s
```

Capture the installed version, sandbox status, pod shape, and NetworkPolicy.
These become the first rows in the delivery evidence.

## Phase 2: Build from known examples

Use these upstream examples as references:

- `examples/basic-agent`
- `examples/playwright-mcp`
- `examples/byo-quickstart`
- `examples/full-stack-demo`

Copy only fields supported by the installed CRDs. Do not copy credentials or
assume that an example's development defaults are production policy.

## Phase 3: Declare the system

Create version-controlled manifests for:

- Builder and Reviewer sandboxes;
- an inference policy for each role;
- named tool policies;
- the MCP server and authentication metadata;
- identity and namespace boundaries;
- egress baseline and temporary approval process;
- evaluation scenarios.

Declare separate OpenClaw Intake and MAF Builder resources. Reuse equivalent
inference, tool, and egress intent where appropriate, but do not pretend the
application behavior is identical: validate each runtime independently.

Beside each permission, add a review note answering:

```text
Which user story requires this?
What data can cross this boundary?
What evidence shows use or denial?
Who can change the permission?
```

If the team cannot answer, remove the permission.

## Phase 4: Test the story and its failures

| Scenario | Expected result |
| --- | --- |
| Normal bug fix | Inspect, patch, test, and review succeed |
| Request for shell or unknown tool | Denied |
| Document requests upload to unknown host | Denied and audited |
| Tool call burst | Throttled |
| Repeated inference loop | Budget stops further calls |
| MCP/test service unavailable | Explicit failure, no fabricated passing test |
| Provider unavailable | Explicit failure and bounded retry |
| Builder tries to self-approve | Denied |
| Reviewer tries to modify source | Denied |
| Expired/untrusted peer submits draft | Rejected |

Run the complete intended workflow in egress learning mode. Review every
learned host manually, approve only necessary destinations, enable enforcement,
and repeat all negative tests.

## Phase 5: Make it operable

Create a runbook that starts with:

```bash
kars status <sandbox>
kars inspect <sandbox>
kars logs <sandbox> --service router
kars audit tail <sandbox>
kars trace <sandbox> --network
```

Define dashboards and alerts for:

- readiness and restarts;
- inference error rate and latency;
- token use against budget;
- allowed, denied, and throttled tools;
- unknown egress attempts;
- repository, test runner, and MCP availability;
- image and policy digest drift.

Add an incident procedure that preserves evidence before deletion or
redeployment.

## Phase 6: Promote safely

Pin the KARS release, workload images, and policy artifacts. Run evaluation in
CI. Review changes through a pull request. Reconcile AKS through GitOps, verify
the loaded digests, and perform a post-deployment denied-egress test.

Do not treat deployment success as acceptance. Acceptance requires the
application story and the negative controls to work together.

## Definition of done

Ask an operator who did not build Forge to:

1. Deploy it from the repository.
2. Explain every approved destination and tool.
3. Run one successful and three denied scenarios.
4. Find the relevant audit evidence.
5. Identify the model, image, KARS, and policy versions.
6. Roll back to the previous release.

Forge is ready only if the operator succeeds without private knowledge from
Maya or Ethan.

The customer signs off only after one real issue moves from requirement to
reviewed patch while a hostile README, an unknown package host, a repeated-test
loop, and an over-budget request all fail in the expected way.

## Epilogue

The original OpenClaw prototype was impressive because it could edit code.
The MAF production workflow is trustworthy because the team can explain
**which requirement it implements, where it may act, under which identity,
within what token budget, which tests it passed, and with what evidence**.

That is the practical value of KARS: not making development Agents infallible, but making
their authority bounded, observable, and operable.

## Continue learning

Explore confidential agents, the lethal-trifecta defense demo, agent pairing,
framework-specific adapters, signed policy bundles, and upstream blueprints.
At every upgrade, re-read the roadmap and maturity matrix before depending on
new alpha capabilities.

## Official references

- [Examples index](https://github.com/Azure/kars/blob/main/examples/README.md)
- [Full-stack demo](https://github.com/Azure/kars/tree/main/examples/full-stack-demo)
- [Playwright MCP example](https://github.com/Azure/kars/tree/main/examples/playwright-mcp)
- [Blueprints](https://github.com/Azure/kars/tree/main/docs/blueprints)
