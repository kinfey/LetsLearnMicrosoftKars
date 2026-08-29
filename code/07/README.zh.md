# KARS AKS 与 Multi-Agent Promotion 实验

[English](README.md) | [简体中文](README.zh.md)

本实验从 [`code/01`](../01/) 的 OpenClaw Forge Contract、
[`code/05`](../05/) 的 GPT-5.6-Sol BYO Runtime，以及
[`code/06`](../06/) 的安全与恢复证据开始。它准备一条经过评审的 AKS Promotion
路径，同时禁止同一个 Agent 编写并批准自己的变更：

```text
OpenClaw Intake
    -> 已批准 FORMAT-482 Contract
    -> Forge Builder（Patch + Targeted Test）
    -> Digest-pinned Handoff Envelope
    -> Forge Reviewer（读取证据 + Approve/Reject）
    -> Human-reviewed GitOps Promotion
    -> KARS on AKS
```

默认运行有意采用 **Plan-only**。它执行 KARS `up --dry-run`，用 Live Local KARS
CRD 验证 GitOps Resource，不创建任何 Azure Resource。真实 AKS Deployment 必须
明确 Opt-in，因为它会创建产生费用的基础设施。

## 默认与可选 Azure 参数

| Variable | 默认值 | 含义 |
| --- | --- | --- |
| `AZURE_RESOURCE_GROUP` | `rg-kinfey` | Azure Resource Group |
| `AKS_NAME` | `aks-kars-demo` | AKS Cluster 名称 |
| `AZURE_LOCATION` | 已存在 Resource Group 的 Location，否则 `eastus2` | Azure Region |
| `KARS_SANDBOX_NAME` | `forge-intake` | `kars up` 创建的初始 OpenClaw Sandbox |
| `KARS_RELEASE` | `v0.1.25` | 固定 KARS Release |
| `KARS_ISOLATION` | `enhanced` | KARS Isolation Level |
| `KARS_MESH_TRUST` | `anonymous` | 初始 Mesh Trust Mode |
| `GITHUB_COPILOT_MODEL` | `gpt-5.6-sol` | 指定模型 |
| `DEPLOY_AKS` | `false` | 真实 Azure 创建开关 |
| `FORGE_IMAGE` | Local Development Image | BYO Image；部署时必须使用 ACR Digest |

`rg-kinfey` 被解释为 Resource Group 名称，而不是 Azure Region。完整运行中，这个
已存在的 Resource Group 自动解析到 `swedencentral`。

如需修改参数但不提交：

```bash
cp config/aks.env.example config/aks.env
```

`config/aks.env` 已加入 Git Ignore。

## Plan-only 实验要证明什么

- `code/05` 仍为 `Running`，并保持原始 1024 Token Policy。
- `code/06` 的 BYO Exec Admission Guard 已安装。
- npm、PyPI 和 NuGet 使用 Microsoft Package Feed Proxy。
- Promotion 前，Host-side Microsoft Agent Framework
  `GitHubCopilotAgent` 会执行真实 GPT-5.6-Sol Tool Call。
- Handoff Contract 固定 Patch 与 Test Evidence SHA-256 Digest。
- Builder 可以提出 Patch，但不能批准 Release。
- Reviewer 可以读取和评审 Builder Evidence，但不能修改 Source，也不能批准自己
  生成的 Artifact。
- Builder 和 Reviewer 使用独立的 `KarsSandbox`、`InferencePolicy` 与
  `ToolPolicy`。
- Reviewer 的 Inference Budget 更小。
- 两个角色都保留 BYO v1 Contract、Strict Egress、Enhanced Isolation、
  Read-only Root Filesystem 与 GPT-5.6-Sol。
- Live KARS API Server 使用 `kubectl apply --dry-run=server` 接受全部六个
  Resource。
- KARS `0.1.25` 针对目标 Azure 参数完成 `kars up --dry-run`。
- 真实部署必须明确启用，并使用按 SHA-256 Digest 固定的 ACR Image，否则会被拒绝。
- Promotion Record 关联 Source Git Commit、code/05 Image Digest、code/06
  Loaded Policy Digest 与目标 AKS 参数。

## 不创建 Azure Resource 的运行方式

```bash
cd code/07
make test
```

已完成的默认运行解析为：

```text
Resource group: rg-kinfey
AKS cluster:    aks-kars-demo
Location:       swedencentral
Model:          gpt-5.6-sol
KARS release:   v0.1.25
Azure created:  no
```

成功输出最后是：

```text
All plan-only AKS and multi-agent checks passed.
No Azure resources were created.
Evidence: .../code/07/.evidence/<UTC timestamp>
```

可单独执行：

```bash
make unit
make plan
make validate
```

## GitOps 权限拆分

渲染后的文件是 `rendered/multi-agent.yaml`。

| 控制 | Builder | Reviewer |
| --- | --- | --- |
| Sandbox | `forge-builder` | `forge-reviewer` |
| Per-request Budget | 2048 | 512 |
| Daily Budget | 8192 | 2048 |
| Patch Source | 通过 Named Workspace Action 允许 | 不存在 |
| Review Decision | 不存在 | Named Review Action |
| Approval Mode | Tool Gate 为 `never` | `always` |
| Trust Threshold | 700 | 800 |

传递 Handoff Envelope 不会把 Builder 的 Workspace、Credential 或 Tool
Authority 交给 Reviewer。

## AKS Day-0 与 Day-1 决策

计划把基础设施创建交给当前 KARS `up` Workflow。Dry-run 报告它会处理 AKS、ACR、
Key Vault、Model Infrastructure、Azure Monitor、Workload Identity、Firewall、
Helm 和初始 Sandbox。

真实部署前必须评审：

- **Day 0：** Azure Location、Address Space/Network Architecture、API
  Exposure、Isolation Level、Node/Region Quota 与 Identity Topology。
- **Day 1：** GitOps Reconciliation、External Audit Export、Monitoring、
  Maintenance Window、Policy Rollout、Rollback 与 code/06 Recovery
  Procedure。

生产环境默认建议 Azure CNI Overlay/Cilium 与 Workload Identity，除非环境有明确
记录的原因选择其他 Day-0 Design。必须检查 KARS 实际创建的 Cluster，不能把 CLI
Plan 当作每个 Network Setting 已经验证。

## 真实 Azure Deployment

先把 BYO Image 推送到 ACR，并按 Digest 固定。随后评审
`.evidence/<run>/aks-plan.json`、渲染后的 Manifest、Quota 与 Cost。

```bash
cp config/aks.env.example config/aks.env
# 编辑 config/aks.env：
# DEPLOY_AKS=true
# FORGE_IMAGE=<acr>.azurecr.io/forge-byo@sha256:<digest>

make deploy
```

`make deploy` 会执行非 Dry-run `kars up`、获取 AKS Credential，并应用经过评审的
Builder/Reviewer Resource。如果 `DEPLOY_AKS` 不严格等于 `true`，或
`FORGE_IMAGE` 没有按 Digest 固定，脚本会拒绝部署。

Repository 和 Evidence 不保存 Subscription ID、Credential 或 Secret Value。

## Mesh 与 A2A 范围

已安装的 KARS CLI 提供 `mesh`、`pair` 与 `a2a` 命令，当前上游 KARS 也记录
Cluster Federation 和 A2A Ingress。本实验使用 `registryMode: local` 和确定性的
Reviewed Handoff Envelope，不会声称已经执行 Cross-cluster Pairing、Public A2A
Ingress、Entra Mesh Trust 或 Encrypted Relay Delivery。

这些能力必须在独立验证 Trust、Expiry、Replay、Ingress、Dual-policy 和 Audit 后
才启用。Connectivity 不等于 Authorization。

## Evidence

每次运行会写入：

```text
.evidence/<UTC timestamp>/
├── transcript.log
├── host-copilot-agent.json
├── gitops-server-dry-run.txt
├── aks-plan.json
├── kars-up-command.txt
├── kars-up-dry-run.txt
├── deploy-opt-in-denial.txt
├── deploy-image-denial.txt
└── promotion-record.json
```

## 平台支持

完整运行已经在 macOS arm64 验证。继承的脚本支持 macOS amd64 和 Linux amd64。
Windows amd64 请在 Ubuntu WSL2 内运行，并启用 Docker Desktop WSL Integration；
Azure CLI、kubectl、Helm、Node.js 22 和 KARS CLI 也应安装在 WSL2 内。

## 参考

- [Azure/KARS Getting Started](https://github.com/Azure/kars/blob/main/docs/getting-started.md)
- [Azure/KARS Enterprise Self-hosted Blueprint](https://github.com/Azure/kars/blob/main/docs/blueprints/03-enterprise-self-hosted.md)
- [Azure/KARS Cross-org Federation Blueprint](https://github.com/Azure/kars/blob/main/docs/blueprints/05-cross-org-federation.md)
- [Azure/KARS CRD Reference](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md)
- [Microsoft Agent Framework GitHub Copilot Samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/providers/github_copilot)
- [Microsoft Agent Framework Build Your Own Claw](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/harness/build_your_own_claw)
- [Azure CNI Overlay](https://learn.microsoft.com/azure/aks/azure-cni-overlay)
