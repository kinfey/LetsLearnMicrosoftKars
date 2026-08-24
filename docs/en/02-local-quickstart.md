# 2. Reproducing Forge in a Safe Local Lab

## Monday morning

Maya wants to connect Forge to the production monorepo immediately. Ethan stops
her.

"First we need a repeatable environment. If we cannot see the router, pod, and
policy boundary locally, we will debug the application and the platform at the
same time."

They agree on one chapter outcome: start a KARS sandbox, inspect its actual
Kubernetes shape, send one request, and remove the environment cleanly.

## Prepare the workstation

The recommended learning path uses local Kubernetes. On macOS or Linux, verify:

```bash
node --version              # Node.js 22+
docker version              # or a compatible container engine
kind version
kubectl version --client
```

The team also needs one inference option:

- GitHub Copilot with an active seat and device login;
- Azure AI Foundry/Azure OpenAI with endpoint, deployment, and credential;
- GitHub Models with a token carrying `models:read`.

They choose Copilot for the first local run because it avoids placing an Azure
service credential in the lab.

## Install a known CLI version

```bash
npm install --global @kars-runtime/cli
kars --version
kars dev --help
```

Maya records both the guide version and installed version in her lab notes.
Flags can change while KARS remains alpha.

## Create the local Kubernetes environment

```bash
kars dev --release v0.1.25 --target local-k8s
```

The command creates a kind cluster, installs the KARS components, and starts a
development sandbox. Maya completes the provider authentication prompt.

Instead of connecting immediately, Ethan asks her to inspect what was created:

```bash
kubectl get namespaces
kubectl get pods -n kars-system
kubectl get networkpolicy -n kars-system
kars list
kars status dev-agent
kars inspect dev-agent
```

They look for three facts:

1. The sandbox reaches `Ready`.
2. Agent and router run as separate containers in the Kubernetes pod shape.
3. Network policy exists; the router is not just a library imported by Forge.

## Follow the first conversation

Now Maya connects:

```bash
kars connect dev-agent
```

She asks:

```text
You are Forge, a development Agent. Explain why an Agent that reads untrusted
repository content should not own GitHub or model credentials. Do not call a tool.
```

While the request runs, Ethan watches the router:

```bash
kars logs dev-agent --service router -f
```

The useful lesson is not the generated paragraph. It is the relationship
between the user's request, the Agent container, the router event, and the
model response.

## Break the lab deliberately

Lina asks Maya to test failure before success becomes familiar.

First, they stop provider authentication or temporarily use an invalid
deployment. They expect a visible 401/403 or provider error—not an invented
answer and not an infinite retry loop.

Then they inspect:

```bash
kars status dev-agent
kars logs dev-agent --service router
kubectl get events -n kars-system --sort-by=.lastTimestamp
```

The team uses this triage order:

| Symptom | Evidence to inspect first |
| --- | --- |
| `kars` not found | npm global binary location and `PATH` |
| kind cluster fails | Container engine availability |
| Pod stays Pending | Kubernetes events and scheduling messages |
| Sandbox is Degraded | `KarsSandbox.status.conditions` |
| Inference returns 401/403 | Provider identity, endpoint, and deployment |
| Router is unavailable | Router container logs and readiness |
| Documented flag fails | Installed version and command-specific help |

This order prevents them from "fixing" application code when the failure is
actually identity or reconciliation.

## Compare with Docker mode

For a quick demonstration, they also run:

```bash
kars dev down
kars dev --release v0.1.25
```

The response looks similar, but the deployment does not provide the same
container separation or Kubernetes NetworkPolicy. Maya writes in the test
report:

> Docker mode proves that the development prompt starts. It does not prove
> source-code or production isolation.

They return to local Kubernetes for the rest of the course.

## Clean up without ambiguity

```bash
kars dev down
```

If cleanup reports an error, they inspect the kind clusters and KARS status
before deleting anything manually. Repeatable creation and cleanup are part of
the product, not housekeeping.

## Lab deliverable

Create a short evidence table:

| Evidence | Command | What it proves |
| --- | --- | --- |
| Sandbox condition | `kars status dev-agent` | Controller reconciliation result |
| Pod containers | `kubectl get/describe pod` | Agent/router deployment shape |
| NetworkPolicy | `kubectl get networkpolicy` | Kubernetes network control exists |
| Router event | `kars logs ... --service router` | Inference uses mediated path |
| Failure output | Invalid provider test | Errors are explicit and observable |

The next chapter replaces the generated development sandbox with resources the
team can review in Git.

## Official references

- [Quickstart](https://github.com/Azure/kars/blob/main/docs/quickstart.md)
- [Getting started](https://github.com/Azure/kars/blob/main/docs/getting-started.md)
- [CLI reference](https://github.com/Azure/kars/blob/main/docs/cli-reference.md)
