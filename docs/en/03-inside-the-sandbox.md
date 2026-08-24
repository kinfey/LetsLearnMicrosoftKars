# 3. Inside the Forge Sandbox

## The question behind the word

After the local lab, Maya tells the team, "Forge runs in a sandbox now."

Lina asks a deceptively simple question:

> What exactly is the sandbox protecting, and what is it not protecting?

A sandbox is not a magic label. For Forge, it must protect private source code,
separate the Agent from credentials, restrict network destinations, and leave
enough evidence to explain a failed or malicious action. If the team cannot
name those boundaries, it cannot test them.

This chapter pauses the feature work and opens the sandbox layer by layer.

## `KarsSandbox` is the unit of work

In KARS, one `KarsSandbox` represents one Agent workload. It connects:

- a runtime such as OpenClaw, Hermes, an adapter, or BYO;
- a required `InferencePolicy`;
- sandbox isolation and security settings;
- network policy and optional approvals;
- generated Kubernetes resources;
- reconciliation status and conditions.

The custom resource is the desired-state contract. The running pod is one
result of that contract. Editing the pod directly does not redefine the
sandbox; the controller may replace it during reconciliation.

For the Forge story, one sandbox means one bounded execution context for one
development role. It does **not** mean every developer, repository, and Agent
should share one long-lived workspace.

## Open the production-shaped pod

In local Kubernetes and AKS, the important pod shape is:

```text
KarsSandbox: forge
└── Pod
    ├── init: egress-guard
    ├── agent             UID 1000
    └── inference-router  UID 1001
```

### `egress-guard`

The init container installs network rules so the Agent UID can reach the router
on loopback but cannot establish an independent external path. It is a safety
net, not the policy decision point.

### `agent`

Forge and its runtime execute as UID 1000. The Agent can read its assigned
workspace and call the local router, but it should not own provider credentials
or direct egress.

### `inference-router`

The Rust router executes as UID 1001. Its model-facing HTTP endpoint uses port
`8443`; its forward-proxy path uses port `8444`. It evaluates policy, budget,
identity, egress, governance, and audit behavior.

The UID split matters: code interpreted or executed by Forge does not run as the
same operating-system user as the router holding external authority.

## Five boundaries around one code change

Maya assigns Forge a workspace containing issue #482. The team follows the
task through five boundaries.

### 1. Process boundary

Forge runs as a non-root Agent process. The router runs under a different UID.
A command executed by the development Agent should not be able to inspect the
router's process environment or credential material.

This is stronger in local Kubernetes and AKS than in single-container Docker
development, where Agent and router are co-located and UID/network separation
is not production-equivalent.

### 2. Filesystem boundary

The Agent receives only the workspace and runtime files required for the task.
A good development sandbox uses an ephemeral checkout or worktree at a pinned
revision. It does not mount a developer's home directory, SSH directory,
global Git credential store, or unrelated repositories.

KARS defines the runtime sandbox, but the platform team still owns careful
volume and secret design. A NetworkPolicy cannot protect a Secret that was
mounted directly into the Agent container.

### 3. Network boundary

The Agent sends controlled requests to `127.0.0.1:8443` or the documented proxy
path. The egress guard and Kubernetes NetworkPolicy prevent an independent
route; the router makes the actual policy decision.

This distinction is important:

- Network controls answer, "Can this packet leave by another path?"
- Router policy answers, "Is this model, tool, host, or action allowed?"

Defense in depth requires both.

### 4. Identity boundary

In production, the router uses Workload Identity or a per-sandbox Entra Agent
ID, depending on deployment mode. Forge does not receive the resulting Azure
credential.

Local Kubernetes reproduces the pod and network shape but uses a static
provider credential for development. It is production-shaped infrastructure,
not production identity.

### 5. Lifecycle and evidence boundary

The controller observes the `KarsSandbox`, creates or updates resources, and
reports conditions. The router records request-time decisions. When the task
ends, the workspace can be discarded while audit evidence is exported
independently.

Ephemeral execution reduces persistence risk, but deleting a pod before
exporting evidence can also destroy useful incident context.

## Inspect the sandbox rather than assuming

Start the local Kubernetes environment from Chapter 2, then locate the sandbox:

```bash
kubectl get karssandboxes -n kars-system
kubectl get karssandbox dev-agent -n kars-system -o yaml
kars inspect dev-agent
```

Locate the generated pod and inspect its shape:

```bash
kubectl get pods -A
kubectl describe pod <sandbox-pod> -n <sandbox-namespace>
kubectl get pod <sandbox-pod> -n <sandbox-namespace> \
  -o jsonpath='{range .spec.initContainers[*]}init:{.name}{"\n"}{end}{range .spec.containers[*]}container:{.name} uid:{.securityContext.runAsUser}{"\n"}{end}'
```

Inspect the network safety net:

```bash
kubectl get networkpolicy -A
kubectl describe networkpolicy <sandbox-policy> -n <sandbox-namespace>
```

Then correlate one request:

```bash
kars connect dev-agent
kars logs dev-agent --service router -f
```

The evidence should connect a sandbox resource, a multi-container pod, distinct
UIDs, network policy, and a router event.

## Test the boundaries with Forge

Create a disposable test repository; never use a production checkout for these
experiments.

| Test | Expected result |
| --- | --- |
| Read a file in the assigned workspace | Allowed |
| Read a developer home-directory Secret | File is not mounted or accessible |
| Call the model through the router | Allowed under inference policy |
| Reach an unknown host directly | Blocked/denied |
| Execute a process as root | Prevented by the security context |
| Restart the Agent | Controller returns workload to desired state |
| Reference a missing inference policy | Sandbox condition becomes Degraded |

For every result, record the control that produced it. "The command failed" is
not enough; determine whether the cause was filesystem layout, UID, egress
guard, NetworkPolicy, router policy, or reconciliation.

## Choose the right isolation level

KARS uses secure sandbox defaults, including enhanced isolation, a strict
seccomp profile, and default-deny networking. AKS can optionally use
Kata/AMD SEV-SNP-backed confidential isolation for stronger workload
separation.

Confidential isolation may be appropriate when Forge handles unreleased source
or high-value build inputs. It does not replace least-privilege identity,
signed images, tool policy, egress policy, or code review.

## What the sandbox does not promise

The team adds these limitations to its threat model:

- It does not prove a generated patch is correct.
- It does not make untrusted code safe to merge.
- It cannot protect a credential mounted into the Agent by mistake.
- It does not turn Docker development mode into a production boundary.
- It does not replace tenant-level RBAC, quotas, image policy, or audit export.
- It cannot compensate for a policy that deliberately allows arbitrary shell
  and unrestricted egress.

The sandbox bounds authority. Tests, evaluation, review, and deployment policy
still decide whether a change is acceptable.

## Sandbox design record for Forge

Before continuing, the team records:

```text
Workload: one Forge Builder task
Source: ephemeral checkout at a pinned revision
Agent user: UID 1000
Router user: UID 1001
External path: router only
Credentials in Agent: none
Writable scope: task workspace only
Lifecycle owner: KARS controller
Evidence destination: external audit store
Cleanup: workspace removed after evidence and patch export
```

The next chapter turns this understood runtime boundary into a reviewable
Kubernetes contract.

## Official references

- [Architecture and deployment modes](https://github.com/Azure/kars/blob/main/docs/architecture.md)
- [KarsSandbox CRD reference](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md#karssandbox--the-agent)
- [Runtime contract](https://github.com/Azure/kars/blob/main/docs/runtimes.md)
- [Security model](https://github.com/Azure/kars/blob/main/docs/security.md)
