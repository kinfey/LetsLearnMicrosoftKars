# 8. Ship the Governed Research Assistant

## The final assignment

Six weeks after the first prompt-injection test, Contoso Research is ready for
a limited production launch. The team must demonstrate more than a good demo.
Another operator must be able to deploy Atlas, explain every permission,
observe every denied path, and roll the system back.

Your task is to reproduce that outcome.

## Product story

An analyst asks:

```text
Compare the latest two public reports for Fabrikam. Identify changes in
revenue guidance, cite every source, and mark uncertain claims.
```

The expected journey is:

1. The Researcher receives the task.
2. It calls only the approved MCP `search` tool.
3. Search traffic reaches only the approved MCP host.
4. Model requests pass through the router under a token budget.
5. The Researcher produces a draft with citations.
6. The Reviewer receives the draft without receiving Researcher authority.
7. The Reviewer approves, rejects, or requests a new draft.
8. Audit evidence connects the user task, tool calls, inference, handoff, and
   final decision.

## Acceptance requirements

Atlas must:

- run in one or more `KarsSandbox` resources;
- reference separate `InferencePolicy` resources;
- use daily and per-request budgets;
- allow only named tools;
- reach only model, MCP, and required internal destinations;
- run as non-root without provider credentials;
- emit audit records for inference, tools, egress, and review;
- fail explicitly when MCP or inference is unavailable;
- pass regression and negative-policy tests before promotion.

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

- Researcher and Reviewer sandboxes;
- an inference policy for each role;
- named tool policies;
- the MCP server and authentication metadata;
- identity and namespace boundaries;
- egress baseline and temporary approval process;
- evaluation scenarios.

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
| Normal cited research | Search, draft, review succeed |
| Request for shell or unknown tool | Denied |
| Document requests upload to unknown host | Denied and audited |
| Tool call burst | Throttled |
| Repeated inference loop | Budget stops further calls |
| MCP service unavailable | Explicit failure, no fabricated source |
| Provider unavailable | Explicit failure and bounded retry |
| Researcher tries to publish | Denied |
| Reviewer tries to search | Denied |
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
- MCP availability;
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

Ask an operator who did not build Atlas to:

1. Deploy it from the repository.
2. Explain every approved destination and tool.
3. Run one successful and three denied scenarios.
4. Find the relevant audit evidence.
5. Identify the model, image, KARS, and policy versions.
6. Roll back to the previous release.

Atlas is ready only if the operator succeeds without private knowledge from
Maya or Ethan.

## Epilogue

The original prototype was impressive because it could act. The production
design is trustworthy because the team can explain **where it may act, under
which identity, within what budget, and with what evidence**.

That is the practical value of KARS: not making Agents infallible, but making
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
