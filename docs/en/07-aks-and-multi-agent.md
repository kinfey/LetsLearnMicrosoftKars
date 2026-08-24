# 7. AKS, Identity, and Multi-Agent Systems

## Move to AKS

Prerequisites include Azure CLI, Helm 3.14 or later, an Azure subscription, and
permission to create the required resources.

```bash
az login
az account set --subscription <subscription-id>
kars up \
  --name prod-agent \
  --region swedencentral \
  --release v0.1.25
```

The default mesh tier uses cluster Workload Identity and anonymous mesh
registration. For per-sandbox Entra Agent ID and verified mesh identity:

```bash
kars up \
  --name prod-agent \
  --region swedencentral \
  --release v0.1.25 \
  --mesh-trust=entra
```

The Entra path requires additional tenant permissions. Choose region only
after checking model, AKS, identity, quota, and confidential-compute
availability together.

## Multi-agent controls

KARS provides mesh, pairing, handoff, and A2A surfaces:

```bash
kars mesh setup-trust
kars mesh status
kars pair generate --expires 30d --token-budget 100000
kars a2a list-exposed
kars handoff prod-agent --to cloud
```

Pairing must be scoped by expiry and budget. Agent-to-agent connectivity does
not imply trust: authenticate the peer, authorize the requested action, and
limit the data released.

Signal-based encrypted mesh sessions keep message content opaque to the relay,
but some trust graph and A2A verification paths remain incomplete. Review the
maturity document before production use.

## Confidential and multi-tenant workloads

Use confidential sandbox isolation for workloads whose threat model requires
Kata/SEV-SNP-backed execution. It adds infrastructure requirements and does not
replace application, identity, or egress policy.

For multiple tenants, separate namespaces and identities, apply quotas and
network policy, and prevent one application team from changing another
tenant's governance resources.

## GitOps promotion

1. Validate a pinned version in local Kubernetes.
2. Commit sandbox and policy manifests.
3. Reference images and policy bundles by digest.
4. Run evaluation and policy tests in CI.
5. Promote through pull requests.
6. Let Argo CD or Flux reconcile AKS.
7. Observe readiness and router-loaded policy digests.

## Exercise

Design two agents: a researcher and an approver. Specify identities, allowed
tools, egress, token budgets, pairing expiry, data passed between them, and the
audit evidence required for approval.

## Official references

- [Getting started](https://github.com/Azure/kars/blob/main/docs/getting-started.md)
- [Security](https://github.com/Azure/kars/blob/main/docs/security.md)
- [Use cases](https://github.com/Azure/kars/blob/main/docs/use-cases.md)
- [Maturity](https://github.com/Azure/kars/blob/main/docs/maturity.md)
