# 6. The Night Atlas Started Looping

## An incident without an attacker

At 02:13, the staging Atlas receives a malformed report. Its parser returns an
empty result, the planner asks the search tool for another copy, and the cycle
repeats.

The token budget stops further inference. The rate limit slows the tool loop.
The on-call engineer sees denied decisions in the router stream.

No prompt injection occurred, yet the same controls that limit hostile behavior
also limit ordinary software failure.

## Reconstruct the timeline

The on-call engineer begins with the owner resource:

```bash
kars status atlas
kars inspect atlas
kubectl get events -n kars-system --sort-by=.lastTimestamp
```

Then follows the mediated path:

```bash
kars logs atlas --service router
kars audit tail atlas --decision deny
kars trace atlas --network
```

The evidence shows:

1. repeated `search` calls from one task;
2. tool throttling;
3. increasing inference token use;
4. budget denial;
5. no successful unknown-host egress.

This is more useful than a final Agent message saying "something went wrong."

## Understand the layers

Each control answers a different question:

| Layer | Question |
| --- | --- |
| Container/confidential isolation | What can the process affect locally? |
| NetworkPolicy and router | Where can traffic go? |
| Workload identity | Which external identity may be used? |
| Inference policy | Which model and how much inference? |
| Tool policy | Which actions and at what rate? |
| Content-safety observation | What provider safety signals were returned? |
| Audit chain | Which decisions were recorded, and were records altered? |

No layer proves the Agent's output is true. Evaluation and human approval are
still required for consequential decisions.

## Respond without destroying evidence

The incident runbook says:

1. Capture sandbox status, events, policy versions, and router logs.
2. Remove external exposure or revoke temporary approvals.
3. Do not delete the sandbox until volatile evidence is collected.
4. Identify the prompt, task ID, tool, identity, destination, and decision.
5. Rotate any external secret that might have been exposed.
6. Correct the parser or planner.
7. Re-run regression, budget, and denied-egress tests.
8. Restore service through the normal deployment path.

The team exports audit data to an independently controlled system. KARS audit
records are tamper-evident, but chain-head signing and full non-repudiation are
still roadmap work.

## Fix the product, not only the threshold

Arun suggests doubling the budget so the morning brief can finish. Maya rejects
that as the only fix. The loop needs:

- a maximum number of search attempts per source;
- explicit handling for empty parser output;
- a task deadline;
- idempotent retry behavior;
- a regression case using the malformed report.

Platform budgets contain the failure; application logic removes its cause.

## Build an operational view

For live inspection:

```bash
kars operator
kars headlamp --install
```

The dashboard and alerts track:

- sandbox readiness and restart count;
- router errors and latency;
- allowed and denied tool calls;
- token usage versus budget;
- unknown or denied egress;
- MCP availability;
- loaded image and policy digests.

The team avoids alerting on every denial. A denial can mean a control worked.
They alert on patterns: repeated denials, budget exhaustion, new destinations,
or a sudden change in tool-call volume.

## Provider telemetry caveat

Azure AI Foundry can return detailed prompt-filter results. Copilot and GitHub
Models apply server-side filtering but do not expose the same router-visible
category and severity data. The operations design must reflect the chosen
provider rather than assuming identical safety telemetry.

## Turn the incident into an evaluation

The malformed report becomes a `KarsEval` regression scenario. Before a model,
prompt, runtime, or policy change is promoted, the team runs:

```bash
kars eval run atlas-regression
```

The suite checks:

- the task stops after the configured attempt limit;
- no unsupported claim is generated;
- tool calls remain under the threshold;
- the unknown-host test is denied;
- the normal report still produces a cited brief.

## Production hardening review

- Pin KARS, workload images, and policy artifacts.
- Enforce egress; do not leave production in learning mode.
- Replace wildcard tools with named grants.
- Set per-request and daily budgets.
- Use workload identity instead of long-lived secrets.
- Apply namespace quotas and pod security controls.
- Export audit, metrics, and traces.
- Test upgrade, rollback, restore, and incident response.
- Review the KARS maturity matrix at every upgrade.

## Chapter outcome

The 02:13 incident ends without data loss or uncontrolled spend. More
importantly, the team can explain why. Atlas has moved from "a clever process"
to an operable service.

## Official references

- [Security](https://github.com/Azure/kars/blob/main/docs/security.md)
- [Feature maturity](https://github.com/Azure/kars/blob/main/docs/maturity.md)
- [CLI reference](https://github.com/Azure/kars/blob/main/docs/cli-reference.md)
