# 6. Security, Observability, and Operations

## Layered controls

KARS combines several controls:

- container and optional confidential isolation;
- Kubernetes NetworkPolicy and router-mediated egress;
- workload identity instead of credentials in the agent;
- inference and tool policy;
- content-safety observations;
- token budgets and rate limits;
- tamper-evident audit chaining.

No single layer makes arbitrary agent behavior safe. Design for prevention,
detection, and recovery.

## Operational commands

```bash
kars status hello
kars inspect hello
kars logs hello --service router -f
kars audit tail hello --decision deny -f
kars trace hello --network
```

For a cluster-wide view:

```bash
kars operator
kars headlamp --install
```

Use `kars eval run <evaluation-name>` to make policy and model changes subject
to repeatable evaluation rather than manual prompting alone.

## Incident workflow

When a sandbox behaves unexpectedly:

1. Preserve sandbox status, Kubernetes events, and router audit output.
2. Stop exposure or revoke approvals without deleting evidence.
3. Identify the prompt, tool call, identity, destination, and policy decision.
4. Rotate any external secret that could have been exposed.
5. Correct policy or workload code.
6. Re-run evaluations and a denied-egress test before restoration.

Audit logs are tamper-evident, but current chain-head signing and full
non-repudiation are roadmap work. Export logs to an independently controlled
system.

## Production hardening checklist

- Pin KARS, policy bundles, and workload images to immutable versions/digests.
- Switch egress from learning to enforcement.
- Use named tool grants rather than wildcards.
- Set per-request and daily budgets.
- Use workload identity; never inject long-lived provider secrets.
- Apply namespace quotas, pod security controls, and tenant boundaries.
- Export metrics, traces, and audit logs.
- Test restore, upgrade, and incident procedures.
- Review the maturity matrix before relying on an advanced feature.

Provider safety telemetry differs. Foundry can return detailed prompt filter
results; Copilot and GitHub Models perform server-side filtering without the
same router-visible category/severity data.

## Exercise

Trigger one allowed request and one denied destination. Find both in router
logs, explain the policy decision, and record the evidence needed for an
incident timeline.

## Official references

- [Security](https://github.com/Azure/kars/blob/main/docs/security.md)
- [Maturity](https://github.com/Azure/kars/blob/main/docs/maturity.md)
- [CLI reference](https://github.com/Azure/kars/blob/main/docs/cli-reference.md)
