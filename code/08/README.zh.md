# 第 9 章实验：OpenClaw-first 应用发布项目

本实验把第 6 章 BYO Runtime、第 7 章安全控制和第 8 章 AKS Promotion 组合成可由
其他运维人员复现的 Issue-to-PR Pilot，并部署到现有 AKS。

安全本地验证：

```bash
cd code/08
make test
```

部署到现有环境：

```bash
cp config/azure.env.example config/azure.env
# 设置 DEPLOY_AZURE=true，并评审所有可选 Azure 参数。
make deploy
```

默认复用 Resource Group `rg-kinfey`、AKS `aks-kars-demo`、ACR
`akskarsdemo449845`、KARS `v0.1.25` 与 GPT-5.6-Sol。`rg-kinfey` 是 Resource
Group，不是 Region；脚本会验证现有 AKS 的实际 Location。ACR Task 明确构建
Linux amd64，并按 Digest 部署 Workload。

`make verify` 会运行 OpenClaw Intake、一个真实 GPT-5.6-Sol 成功流程，以及
Shell/未知工具、未知 Egress 与 Builder Self-approval 三个拒绝场景。暂停、
Evidence 保留和 Rollback 请参阅 `RUNBOOK.md`。

Azure 部署已在 amd64 `clawpool` 验证。Application 与 Router Audit Chain 通过，
InferencePolicy Compiled/Loaded Digest 已收敛。`KarsEval` 声明可以解析 Corpus，
但上游 `v0.1.25` Runner Job 因生成的 Pod 缺少 Restricted Security Context 而
被 AKS Restricted Pod Security 阻止。失败 Job 已暂停，没有降低 Namespace
Security。
