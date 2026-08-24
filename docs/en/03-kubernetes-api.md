# 3. Kubernetes API and Core Concepts

## Reconciliation, not scripting

KARS extends Kubernetes with custom resources. You declare the desired agent
and policies; the controller continuously reconciles the required namespace
objects, pod, services, policy projections, and status.

The two essential resources are:

- `KarsSandbox`: runtime, image/configuration, isolation, and policy references.
- `InferencePolicy`: provider, model preference, budgets, and inference controls.

An inference policy is mandatory and must be in the same namespace as its
sandbox.

## Minimal manifest

Save this as `hello.yaml` and adjust the provider/deployment for your account:

```yaml
apiVersion: kars.azure.com/v1alpha1
kind: InferencePolicy
metadata:
  name: hello-inference
  namespace: kars-system
spec:
  appliesTo:
    sandboxName: hello
  modelPreference:
    primary:
      provider: azure-openai
      deployment: gpt-4.1
---
apiVersion: kars.azure.com/v1alpha1
kind: KarsSandbox
metadata:
  name: hello
  namespace: kars-system
spec:
  runtime:
    kind: OpenClaw
    openclaw:
      config:
        agent:
          model: azure/gpt-4.1
  inferenceRef:
    name: hello-inference
```

Apply and observe it:

```bash
kubectl apply -f hello.yaml
kubectl get karssandbox hello -n kars-system -w
kubectl describe karssandbox hello -n kars-system
kars status hello
```

Read `status.conditions` before debugging generated pods. A degraded condition
often explains an invalid runtime or unresolved policy reference more directly.

## Resource map

| Resource | Purpose |
| --- | --- |
| `KarsSandbox` | Agent workload and runtime |
| `InferencePolicy` | Models, budgets, and inference controls |
| `ToolPolicy` | Tool allow rules and rate limits |
| `McpServer` | MCP endpoint and authentication metadata |
| `KarsMemory` | Memory configuration |
| `KarsEval` | Evaluation workloads |
| `TrustGraph` | Mesh trust relationships |
| `EgressApproval` | Time-bounded network approval |
| `KarsSREAction` | Governed operational action |
| `A2AAgent` | Agent-to-agent exposure |

`KarsAuthConfig` and `KarsPairing` are infrastructure-managed resources. Do not
treat every CRD as equally mature; check the upstream maturity table.

## Declarative workflow

Use `kubectl diff -f hello.yaml` before applying changes. In shared
environments, store manifests in Git and let Argo CD or Flux reconcile them.
Avoid mixing imperative CLI mutations and GitOps ownership of the same fields.

## Exercise

1. Deploy the manifest.
2. Change the deployment name to an invalid value.
3. Observe sandbox and router status.
4. Restore the valid value and confirm reconciliation.
5. Delete the resources with `kubectl delete -f hello.yaml`.

## Official references

- [CRD reference](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md)
- [Basic agent example](https://github.com/Azure/kars/tree/main/examples/basic-agent)
- [Architecture](https://github.com/Azure/kars/blob/main/docs/architecture.md)
