# Chapter 9 lab: OpenClaw-first applied release project

This lab turns the Chapter 6 BYO runtime, Chapter 7 controls, and Chapter 8 AKS
promotion into a reproducible Issue-to-PR pilot on the existing AKS cluster.

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
Task explicitly builds Linux amd64 and the workload is applied by digest.

`make verify` runs the OpenClaw Intake, one successful GPT-5.6-Sol workflow,
and denials for shell/unknown tools, unknown egress, and Builder
self-approval. See `RUNBOOK.md` for suspension, evidence, and rollback.

The Azure deployment was verified on the amd64 `clawpool`. The application and
Router audit chains passed, and the InferencePolicy Compiled/Loaded Digests
converged. The `KarsEval` declaration resolves its corpus, but the upstream
`v0.1.25` Runner Job is blocked by AKS restricted Pod Security because its
generated Pod lacks the required restricted security context. The Job is
suspended; the namespace policy is not weakened.
