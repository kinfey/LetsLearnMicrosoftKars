# 8. AKS 与 Multi-Agent Promotion：分离构建与批准

> **交付阶段：** 规划并评审 AKS 生产 Promotion
> **起点：** OpenClaw Forge、第 6 章 GPT-5.6-Sol BYO Runtime，以及第 7 章
> Security/Recovery Evidence
> **可执行实验：** [`code/07`](../../code/07/)

## 一切仍然从 OpenClaw 开始

OpenClaw 建立最初的 FORMAT-482 Issue-to-Patch 行为。第 6 章改变 Runtime，第 7
章让运维控制可以测量，但业务 Contract 没有改变：

```text
OpenClaw Intake
    -> 已批准 Issue 与 Acceptance Criteria
    -> Forge Builder
    -> Patch Digest + Test-evidence Digest
    -> Forge Reviewer
    -> Human-reviewed GitOps Change
    -> KARS on AKS
```

Multi-Agent Design 不是两个 Prompt 互相聊天，而是 Identity、Tool、Budget、Data 与
Approval Authority 的分离。

## 运行安全默认路径

```bash
cd code/07
make test
```

默认运行不会创建 Azure Resource。它会：

1. 确认 `code/05` BYO Runtime 与 `code/06` Security Guard；
2. 检查 Microsoft npm、PyPI 与 NuGet Source；
3. 运行确定性的 Builder/Reviewer Authorization Test；
4. 通过 Host Microsoft Agent Framework `GitHubCopilotAgent` 调用
   GPT-5.6-Sol；
5. 渲染两个独立的 KARS Sandbox 与 Policy；
6. 使用 Live KARS API Server 执行 Server-side Dry-run；
7. 执行官方 KARS `up --dry-run`；
8. 证明真实部署必须明确 Opt-in，并使用按 Digest 固定的 ACR Image；
9. 创建关联 Source Image 与 Policy Digest 的 Promotion Record。

完整 macOS arm64 运行全部通过，且没有创建 Azure Resource。

## 正确解释指定的 Azure 参数

实验使用：

| 参数 | 默认值 |
| --- | --- |
| Resource Group | `rg-kinfey` |
| AKS Cluster | `aks-kars-demo` |
| Azure Location | 已存在 Resource Group 的 Location，否则 `eastus2` |
| Model | `gpt-5.6-sol` |
| KARS Release | `v0.1.25` |
| Isolation | `enhanced` |

`rg-kinfey` 是 Resource Group 名称，不是 Azure Region。只读查询发现该 Group
存在于 `swedencentral`，所以生成的 Plan 使用这个 Location。

所有值均可选，可以在 Git Ignore 的 `code/07/config/aks.env` 中修改。

## 把 Plan-only 作为 Deployment Gate

生成的命令是：

```bash
kars up \
  --name forge-intake \
  --model gpt-5.6-sol \
  --policy developer \
  --region swedencentral \
  --cluster-name aks-kars-demo \
  --resource-group rg-kinfey \
  --isolation enhanced \
  --release v0.1.25 \
  --mesh-trust anonymous \
  --dry-run \
  --yes
```

KARS 报告真实运行将检查 Azure Credential，部署 AKS、ACR、Key Vault、Model
Infrastructure、Azure Monitor 与 Workload Identity，配置 Firewall 与 ACR
Attachment，安装 KARS Control Plane，创建 Federated Credential，并等待初始
Sandbox。

Dry-run 证明 Command Resolution 与 Preflight，不证明未来 Cluster 的 Quota、
Capacity、Model Availability、Network Routing 或 Runtime Health。

## 分离 Builder 与 Reviewer Authority

`code/07/operations/handoff.py` 定义 Digest-pinned Handoff Envelope。测试要求：

- Builder 可以提出 Patch，但不能批准 Release。
- Reviewer 可以评审并批准 Builder Artifact。
- Reviewer 不能修改 Source。
- Reviewer 不能批准 Reviewer 自己产生的 Artifact。
- 错误 Model 或没有固定 Evidence 的请求会被拒绝。

Handoff 只包含 Reference 与 Digest，不包含可复用 Credential 或 Builder 的可写
Workspace。

## 渲染独立 KARS Resource

GitOps Template 生成：

| Resource | Builder | Reviewer |
| --- | --- | --- |
| `KarsSandbox` | `forge-builder` | `forge-reviewer` |
| `InferencePolicy` | `forge-builder-inference` | `forge-reviewer-inference` |
| `ToolPolicy` | `forge-builder-tools` | `forge-reviewer-tools` |
| Per-request Token | 2048 | 512 |
| Daily Token | 8192 | 2048 |
| Tool Authority | Read/Search/Patch/Test/Diff | Read Diff/Evidence + Submit Decision |
| Approval Mode | `never` | `always` |
| Trust Threshold | 700 | 800 |

两个 Sandbox 都使用：

- `runtime.kind: BYO`；
- `contractVersion: v1`；
- GPT-5.6-Sol；
- Enhanced Isolation；
- Read-only Root Filesystem；
- Strict、Default-deny Egress；
- Local Registry Mode。

Live KARS CRD 在 Server-side Dry-run 中接受全部六个 Resource。实验没有 Apply，
因此不会创建额外 Local Agent Pod。

## 把第 7 章 Evidence 带入 Promotion

Promotion Record 包含：

- Repository Commit；
- KARS Version `0.1.25`；
- Model `gpt-5.6-sol`；
- 正在运行的 code/05 BYO Image Digest；
- code/06 Loaded Policy Digest；
- Target Resource Group、Cluster Name 与 Location；
- `deployed: false`。

Promotion 必须从已知 Runtime 与 Policy Artifact 开始，不能在生产批准过程中重新
构建不可追踪的 Image。

## 评审 AKS Day-0 Decision

移除 `--dry-run` 前必须决定：

- Azure Location 与区域 Quota/Capacity；
- VNet 与 Address Space；
- API Server Access；
- Azure CNI Overlay 或 VNet-routable Pod IP；
- Cilium/Network Policy；
- Static Egress Gateway、Firewall 或 NVA；
- Workload Identity 与 Key Vault Integration；
- System/User Node Pool、Zone 与 VM Size；
- Confidential Isolation Requirement。

这些是 Day-0 Decision，因为其中部分变更需要重建 Cluster。生产设计默认优先
Azure CNI Overlay + Cilium、Workload Identity、Multi-zone 和非 Burstable VM
Family，除非环境存在明确记录的限制。

本实验由 KARS 管理 Infrastructure Workflow。部署后必须检查实际 AKS
Configuration，不能根据成功的 CLI Dry-run 推断每个 Network Property 都已验证。

## 规划 Day-1 Operation

缺少以下内容时，AKS Deployment 仍不完整：

- External Router Audit Export，因为第 7 章已证明 Pod 替换后 Local History 会
  Reset；
- Managed Prometheus、Container Insights、Grafana 与 Control-plane Diagnostic
  Log；
- Maintenance Window 与 Staged Upgrade/Rollback；
- Image Signing 与 Digest Pinning；
- GitOps 对 Production Field 的 Ownership；
- Post-deployment Allow/Denial Test；
- Replicated Service 的 Pod Disruption Budget 与 Topology Spread；
- 使用 Compiled/Loaded Digest 验证 Policy Rollout。

## 只通过明确 Opt-in 部署

把 BYO Image 推送到 ACR 并固定 Digest 后：

```bash
cd code/07
cp config/aks.env.example config/aks.env
```

设置：

```text
DEPLOY_AKS=true
FORGE_IMAGE=<acr>.azurecr.io/forge-byo@sha256:<digest>
```

然后：

```bash
make deploy
```

如果 Switch 不严格等于 `true`，或 Image 没有按 Digest 固定，脚本会拒绝执行。
随后脚本才运行非 Dry-run `kars up`、获取 AKS Credential、渲染并应用经过评审的
Resource。

Repository 不会写入 Subscription ID 或 Credential。

## 不夸大 Mesh 或 A2A

KARS `0.1.25` 提供 `mesh`、`pair` 与 `a2a` CLI Surface，当前上游 Blueprint
也记录 Federation。本实验有意使用 `registryMode: local` 和 Reviewed
Application Handoff Contract。

实验不会声称已执行 Cross-cluster Pairing、Entra Mesh Trust、Public A2A、
Encrypted Relay、Token Expiry、Replay Defense 或 Dual-cluster Audit。这些能力
需要两个独立 Trust Domain 和明确的 Negative Test。

## 平台支持

完整运行使用 macOS arm64。macOS amd64 与 Linux amd64 使用相同脚本。Windows
amd64 请在 Ubuntu WSL2 内运行，启用 Docker Desktop WSL Integration，并把全部
CLI 安装在 WSL2 内。

## 完成定义

只有当 OpenClaw Requirement 仍可追踪、Builder 无法 Self-approve、Reviewer
不能编辑 Source、Runtime 与 Policy Artifact 均按 Digest 固定、AKS Day-0 Choice
已评审、GitOps Resource 通过 Admission、External Audit 与 Rollback 已准备，并且
Post-deployment Test 证明一条允许 Workflow 与一条被拒绝的 Authority Violation
时，AKS Promotion 才算 Ready。

## 官方参考

- [KARS Getting Started](https://github.com/Azure/kars/blob/main/docs/getting-started.md)
- [Enterprise Self-hosted Blueprint](https://github.com/Azure/kars/blob/main/docs/blueprints/03-enterprise-self-hosted.md)
- [Cross-org Federation Blueprint](https://github.com/Azure/kars/blob/main/docs/blueprints/05-cross-org-federation.md)
- [KARS CRD Reference](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md)
- [Microsoft Agent Framework GitHub Copilot Samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/providers/github_copilot)
- [Microsoft Agent Framework Build Your Own Claw](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/harness/build_your_own_claw)
- [Azure CNI Overlay](https://learn.microsoft.com/azure/aks/azure-cni-overlay)
