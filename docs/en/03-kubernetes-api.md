# 3. Turning a Demo into a Kubernetes Contract

## The problem with a command transcript

Atlas now works in Maya's local cluster, but nobody can answer a simple review
question: "What exactly did we approve?"

A terminal history contains commands, defaults, retries, and experiments. It
does not describe a stable desired state. Ethan asks the team to express Atlas
as Kubernetes resources that can be reviewed, diffed, and reconciled.

## Start with two responsibilities

The team separates the workload from its inference authority:

- `KarsSandbox` says how Atlas runs.
- `InferencePolicy` says which inference path Atlas may use.

The policy is mandatory and lives in the same namespace as the sandbox. This
prevents an application manifest from silently falling back to unrestricted
inline inference.

## Write the first contract

Create `atlas.yaml`:

```yaml
apiVersion: kars.azure.com/v1alpha1
kind: InferencePolicy
metadata:
  name: atlas-inference
  namespace: kars-system
  labels:
    app.kubernetes.io/name: atlas
spec:
  appliesTo:
    sandboxName: atlas
  modelPreference:
    primary:
      provider: azure-openai
      deployment: gpt-4.1
---
apiVersion: kars.azure.com/v1alpha1
kind: KarsSandbox
metadata:
  name: atlas
  namespace: kars-system
  labels:
    app.kubernetes.io/name: atlas
spec:
  runtime:
    kind: OpenClaw
    openclaw:
      config:
        agent:
          model: azure/gpt-4.1
  inferenceRef:
    name: atlas-inference
```

The provider and deployment are examples; Maya changes them to match the
configured account.

Before applying, the team asks:

- Does the policy target the correct sandbox?
- Does the sandbox reference the correct policy?
- Are both in `kars-system`?
- Is the runtime actually supported by this KARS release?

Then they apply:

```bash
kubectl diff -f atlas.yaml
kubectl apply -f atlas.yaml
kubectl get karssandbox atlas -n kars-system -w
```

## Read status as a conversation

Kubernetes `spec` is the team's request. `status` is the controller's answer.

```bash
kubectl get karssandbox atlas -n kars-system -o yaml
kubectl describe karssandbox atlas -n kars-system
kars status atlas
```

When `Ready=True`, the controller is reporting successful reconciliation—not
that every possible Atlas task is correct or secure.

Lina intentionally changes `inferenceRef.name` to `missing-policy`. The
sandbox becomes degraded. The team reads `status.conditions` before opening pod
logs. The condition identifies the unresolved dependency, so they restore the
reference and watch reconciliation recover.

This experiment teaches a durable debugging rule:

> Read the owner resource's conditions before debugging generated resources.

## Add the rest of the map only when needed

During design review, the team maps future requirements to CRDs:

| Atlas requirement | KARS resource |
| --- | --- |
| Run the research process | `KarsSandbox` |
| Select model and cap inference | `InferencePolicy` |
| Allow only `search` | `ToolPolicy` |
| Register the search service | `McpServer` |
| Persist approved memory | `KarsMemory` |
| Run regression cases | `KarsEval` |
| Model trusted peers | `TrustGraph` |
| Temporarily reach a host | `EgressApproval` |
| Govern an operator action | `KarsSREAction` |
| Expose a peer endpoint | `A2AAgent` |

They do not create every resource "for completeness." Each resource must answer
a concrete requirement, and each advanced feature must be checked against the
upstream maturity table.

## See reconciliation in practice

The team changes the model deployment in Git:

```bash
kubectl diff -f atlas.yaml
kubectl apply -f atlas.yaml
kubectl get karssandbox atlas -n kars-system -w
```

They observe the controller update the generated configuration and status. No
operator edits a generated ConfigMap directly; reconciliation would overwrite
that edit and hide the real source of truth.

## Decide who owns fields

For the local lab, `kubectl apply` is enough. In production, the team plans to
use Argo CD or Flux. They establish one rule early:

> A field has one owner.

If GitOps owns an inference policy, an operator does not use an imperative CLI
command to change the same policy during normal operations. Emergency changes
must be captured back into Git or explicitly reverted.

## Failure scenarios

Test these one at a time:

1. Reference a missing `InferencePolicy`.
2. Put policy and sandbox in different namespaces.
3. Use a runtime not implemented in the installed release.
4. Use an invalid provider deployment.

For each test, record:

- the `KarsSandbox` condition;
- whether a pod was created;
- the router or controller error;
- the smallest manifest change that restores readiness.

## Chapter outcome

Atlas is no longer "whatever Maya typed on Monday." It is a versionable
contract. The next review can discuss a diff rather than a memory.

## Official references

- [CRD reference](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md)
- [Basic agent example](https://github.com/Azure/kars/tree/main/examples/basic-agent)
- [Architecture](https://github.com/Azure/kars/blob/main/docs/architecture.md)
