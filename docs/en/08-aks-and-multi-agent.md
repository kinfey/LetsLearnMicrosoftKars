# 8. From One Sandbox to a Production Team

## Why Forge becomes two Agents

Developers like Forge's patches, but engineering policy will not allow the same
Agent to write a change and approve its merge.

The team splits the workflow:

- **Forge Builder** reads the issue, edits a workspace, and runs targeted tests.
- **Forge Reviewer** inspects the diff and evidence, then approves or rejects
  the proposed pull request.

The separation is useful only if identity, tools, data transfer, and audit
evidence are also separated.

## Prepare the AKS move

Ethan verifies Azure CLI, Helm 3.14+, subscription permissions, regional model
availability, quota, and any confidential-compute requirements.

```bash
az login
az account set --subscription <subscription-id>
kars up \
  --name forge \
  --region swedencentral \
  --release v0.1.25
```

The default mesh path uses cluster Workload Identity and anonymous mesh
registration. For per-sandbox Entra Agent ID and verified mesh identity:

```bash
kars up \
  --name forge \
  --region swedencentral \
  --release v0.1.25 \
  --mesh-trust=entra
```

The Entra option requires additional tenant permissions. Region selection is a
joint decision across AKS, model deployment, identity, quota, and confidential
compute—not simply the nearest region.

## Design the authority split

The team creates a table before deploying:

| Control | Builder | Reviewer |
| --- | --- | --- |
| Identity | Build workload identity | Review workload identity |
| Tools | Read, patch, targeted tests | Read diff/evidence, approve/reject |
| Egress | Model + approved dev-tool MCP | Model + internal review service |
| Write access | Ephemeral workspace/branch | Pull-request review status only |
| Token budget | Higher implementation budget | Smaller review budget |
| Human access | Repository developers | Maintainers |

Passing a diff between Agents does not transfer authority. The Reviewer never
receives the Builder's workspace or write identity.

## Pair and communicate carefully

KARS exposes mesh, pairing, handoff, and A2A workflows:

```bash
kars mesh setup-trust
kars mesh status
kars pair generate --expires 30d --token-budget 100000
kars a2a list-exposed
```

Pairing is bounded by expiry and budget. The message contains the draft,
citations, and task metadata—not environment data or reusable credentials.

Encrypted mesh sessions can keep content opaque to a relay, but connectivity
is not authorization. Some TrustGraph and A2A verification paths remain
incomplete in the current alpha. The team checks the maturity documentation
and adds compensating controls before relying on them.

## Decide whether confidential isolation is needed

A future Forge workload may modify unreleased product source. For that threat
model, the team evaluates confidential sandbox isolation backed by Kata/SEV-SNP.

Confidential execution can strengthen workload isolation, but it does not
replace:

- least-privilege identity;
- tool and egress policy;
- application validation;
- audit export;
- human approval.

## Promote through GitOps

The production sequence is:

1. Pin and validate KARS in local Kubernetes.
2. Commit sandbox, identity, and policy resources.
3. Pin workload images and policy bundles by digest.
4. Run regression and policy tests in CI.
5. Review the pull request with application, platform, and security owners.
6. Let Argo CD or Flux reconcile AKS.
7. Verify sandbox readiness and router-loaded policy digests.
8. Run post-deployment denied-path tests.

The team avoids imperative edits to GitOps-owned fields. An emergency change is
either committed immediately or explicitly rolled back.

## Multi-tenant boundary

When a second business unit adopts KARS, Ethan does not place all Agents in one
shared namespace. The platform separates namespaces, workload identities,
quotas, network policy, RBAC, and policy ownership. An application team cannot
modify another tenant's governance resources.

## Production rehearsal

Before launch, the team rehearses:

1. The Builder submits a minimal patch and passing targeted-test evidence.
2. The Reviewer approves the proposed pull request.
3. An unpaired Agent attempts submission and is rejected.
4. An expired pairing token is rejected.
5. The Builder attempts to approve its own change and is denied.
6. The Reviewer attempts to modify source and is denied.
7. Operators reconstruct the entire workflow from exported evidence.

## Chapter outcome

Forge is now a system of cooperating identities, not two prompts talking to
each other. The architecture preserves separation of duties from Kubernetes
resources through runtime policy and audit.

## Official references

- [Getting started](https://github.com/Azure/kars/blob/main/docs/getting-started.md)
- [Security](https://github.com/Azure/kars/blob/main/docs/security.md)
- [Use cases](https://github.com/Azure/kars/blob/main/docs/use-cases.md)
- [Feature maturity](https://github.com/Azure/kars/blob/main/docs/maturity.md)
