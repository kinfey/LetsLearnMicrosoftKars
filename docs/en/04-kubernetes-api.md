# 4. Platform: Turn the Demo into a Kubernetes Contract

> **Delivery stage:** Shared development platform
> **New problem:** How can every engineer and CI job reproduce the same Forge
> environment?
> **Deliverable:** Reviewable `KarsSandbox` and `InferencePolicy` manifests.

## The problem with a command transcript

The startup adds its first engineer. Forge works in Maya's local cluster, but
nobody can answer a simple review
question: "What exactly did we approve?"

A terminal history contains commands, defaults, retries, and experiments. It
does not describe a stable desired state. Ethan asks the team to express Forge
as Kubernetes resources that can be reviewed, diffed, and reconciled.

## Start with two responsibilities

The team separates the workload from its inference authority:

- `KarsSandbox` says how Forge runs.
- `InferencePolicy` says which inference path Forge may use.

The policy is mandatory and lives in the same namespace as the sandbox. This
prevents an application manifest from silently falling back to unrestricted
inline inference.

## Write the first contract

Create `forge.yaml`:

```yaml
apiVersion: kars.azure.com/v1alpha1
kind: InferencePolicy
metadata:
  name: forge-inference
  namespace: kars-system
  labels:
    app.kubernetes.io/name: forge
spec:
  appliesTo:
    sandboxName: forge
  modelPreference:
    primary:
      provider: azure-openai
      deployment: gpt-4.1
---
apiVersion: kars.azure.com/v1alpha1
kind: KarsSandbox
metadata:
  name: forge
  namespace: kars-system
  labels:
    app.kubernetes.io/name: forge
spec:
  runtime:
    kind: OpenClaw
    openclaw:
      config:
        agent:
          model: azure/gpt-4.1
  inferenceRef:
    name: forge-inference
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
kubectl diff -f forge.yaml
kubectl apply -f forge.yaml
kubectl get karssandbox forge -n kars-system -w
```

## Read status as a conversation

Kubernetes `spec` is the team's request. `status` is the controller's answer.

```bash
kubectl get karssandbox forge -n kars-system -o yaml
kubectl describe karssandbox forge -n kars-system
kars status forge
```

When `Ready=True`, the controller is reporting successful reconciliation—not
that every possible Forge code change is correct or secure.

Lina intentionally changes `inferenceRef.name` to `missing-policy`. The
sandbox becomes degraded. The team reads `status.conditions` before opening pod
logs. The condition identifies the unresolved dependency, so they restore the
reference and watch reconciliation recover.

This experiment teaches a durable debugging rule:

> Read the owner resource's conditions before debugging generated resources.

## Add the rest of the map only when needed

During design review, the team maps future requirements to CRDs:

| Forge requirement | KARS resource |
| --- | --- |
| Run the development process | `KarsSandbox` |
| Select model and cap inference | `InferencePolicy` |
| Allow repository read, patch, and test tools | `ToolPolicy` |
| Register the source-control/tool service | `McpServer` |
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
kubectl diff -f forge.yaml
kubectl apply -f forge.yaml
kubectl get karssandbox forge -n kars-system -w
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

Forge is no longer "whatever Maya typed on Monday." It is a versionable
contract. The next review can discuss a diff rather than a memory.

The same contract can select OpenClaw today and MAF Python later. Runtime code
changes, but the required inference reference, Sandbox controls, router, and
status model remain platform concerns.

## Definition of done

The platform contract is ready when a clean cluster can reconcile it, a missing
policy produces a useful Degraded condition, `kubectl diff` shows every
authority change, and CI—not a founder's shell history—can reproduce it.

## Official references

- [CRD reference](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md)
- [Basic agent example](https://github.com/Azure/kars/tree/main/examples/basic-agent)
- [Architecture](https://github.com/Azure/kars/blob/main/docs/architecture.md)
