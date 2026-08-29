# Chapter 9 lab: OpenClaw-first MAF release project

This lab combines the Chapter 6 MAF pattern, Chapter 7 controls, and Chapter 8
AKS promotion into a reproducible Issue-to-PR pilot on the existing AKS
cluster:

```text
OpenClaw Intake
  -> MAF Agent + OpenAIChatClient + inspect_release_contract @tool
  -> KARS MAF adapter
  -> local KARS Router
  -> GitHub Copilot GPT-5.6-Sol
```

The application contains no direct Router HTTP call. The KARS adapter pins the
MAF OpenAI client to `127.0.0.1:8443`, while the provider credential remains
only in the Router path. The MAF Agent sets `store: false`, so its Responses
API function loop carries tool history inline instead of sending the
`previous_response_id` field that the KARS `v0.1.25` GitHub Copilot adapter
does not support. A small MAF client compatibility subclass also removes the
provider's overlong encrypted Function Call item ID before inline replay while
preserving the standard `call_id`.

Safe local validation:

```bash
cd code/08
make test
```

Deploy to an existing environment:

```bash
cp config/azure.env.example config/azure.env
# Set DEPLOY_AZURE=true and review the optional Azure values.
make deploy
```

The default values reuse resource group `rg-kinfey`, AKS `aks-kars-demo`, ACR
`akskarsdemo449845`, KARS `v0.1.25`, and GPT-5.6-Sol. `rg-kinfey` is a resource
group, not a region; the script verifies the existing AKS location. The ACR
Task explicitly builds Linux amd64 and the MAF runtime is selected by digest.

KARS `v0.1.25` exposes `agentCode.oci` in the CRD/runtime plan but does not yet
materialize that code mount in the Pod. This lab therefore extends the official
KARS MAF Python image, bakes the application into `/opt/fabrikam-agent`, copies
it as UID 1000 into the writable `/sandbox/agent` volume at startup, and sets
the Controller `MAF_RUNTIME_IMAGE` override. The Sandbox remains a first-class
`MicrosoftAgentFramework/python` runtime, not BYO.

`make verify` runs the OpenClaw Intake, one successful GPT-5.6-Sol workflow,
proves exactly one bounded MAF tool call, and checks denials for shell/unknown
tools, unknown egress, and Builder self-approval. See `RUNBOOK.md` for
suspension, evidence, and rollback.

The Azure deployment was verified on the amd64 `clawpool`. The application and
Router audit chains passed, and the InferencePolicy Compiled/Loaded Digests
converged. The `KarsEval` declaration resolves its corpus, but the upstream
`v0.1.25` Runner Job is blocked by AKS restricted Pod Security because its
generated Pod lacks the required restricted security context. The Job is
suspended; the namespace policy is not weakened.
