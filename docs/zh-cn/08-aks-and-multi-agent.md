# 8. 部署：把 Forge 推广到 AKS

> **交付阶段：** CI/CD 与生产部署
> **新问题：** 小型创业团队如何频繁部署，却不允许 Agent 批准、Merge 并发布
> 自己的工作？
> **交付物：** GitOps 推广路径、分离身份与回滚方案。

## 为什么 Forge 变成两个 Agent

Design Partner 接受了 MAF 候选版本。开发者喜欢 Forge 的 Patch，但研发规范
不允许同一个 Agent 既编写变更又批准合并。

团队拆分部署后的工作流：

- **Forge Intake（OpenClaw Canary）** 接收模糊开发需求并帮助完善验收条件，但
  不能修改生产仓库。
- **Forge Builder（MAF Python）** 读取批准的 Issue、编辑临时 Workspace 并
  运行目标测试。
- **Forge Reviewer** 检查 Diff 与测试证据，再批准或拒绝拟议 Pull Request。

创业团队不会假设当前版本的 OpenClaw 与 MAF 具有完全相同的 Mesh 能力。除非
所选 Runtime 路径有明确文档且经过测试，否则 Workflow Handoff 使用已评审的
Service/API 边界。Runtime 宣传不能取代端到端测试。

只有同时分离身份、工具、数据传递与审计证据，这种职责拆分才有意义。

## 准备迁移 AKS

Ethan 检查 Azure CLI、Helm 3.14+、订阅权限、区域模型可用性、配额和机密计算
要求。

```bash
az login
az account set --subscription <subscription-id>
kars up \
  --name forge \
  --region swedencentral \
  --release v0.1.25
```

默认 Mesh 路径使用集群 Workload Identity 和匿名 Mesh 注册。如需每沙箱 Entra
Agent ID 与已验证 Mesh 身份：

```bash
kars up \
  --name forge \
  --region swedencentral \
  --release v0.1.25 \
  --mesh-trust=entra
```

Entra 选项需要额外租户权限。区域选择是 AKS、模型 Deployment、身份、配额与
机密计算的联合决定，而不只是选择最近区域。

## 设计权限拆分

部署前，团队建立表格：

| 控制 | Builder | Reviewer |
| --- | --- | --- |
| 身份 | 构建 Workload Identity | 评审 Workload Identity |
| 工具 | 读取、Patch、目标测试 | 读取 Diff/证据、批准/拒绝 |
| 出口 | 模型 + 批准研发 MCP | 模型 + 内部评审服务 |
| 写入权限 | 临时 Workspace/Branch | 仅 Pull Request Review 状态 |
| Token 预算 | 较高实现预算 | 较小评审预算 |
| 人员访问 | 仓库开发者 | Maintainer |

Agent 间传递 Diff 不会转移权限。Reviewer 永远不会得到 Builder 的 Workspace
或写入身份。

## 谨慎 Pairing 与通信

KARS 提供 Mesh、Pairing、Handoff 和 A2A 工作流：

```bash
kars mesh setup-trust
kars mesh status
kars pair generate --expires 30d --token-budget 100000
kars a2a list-exposed
```

Pairing 受有效期和预算约束。消息只包含草稿、引用和任务元数据，不包含环境数据或
可复用凭据。

加密 Mesh Session 可使内容对 Relay 不透明，但可连接并不等于有权限。当前 alpha
中的部分 TrustGraph 和 A2A 验证路径仍不完整。团队会查看成熟度文档，并在依赖
这些能力前增加补偿控制。

## 是否需要机密隔离

未来 Forge 可能修改尚未发布的产品源码。针对该威胁模型，团队评估由
Kata/SEV-SNP 支持的机密沙箱隔离。

机密执行可以加强工作负载隔离，但不能取代：

- 最小权限身份；
- 工具与出口策略；
- 应用验证；
- 审计导出；
- 人工批准。

## 通过 GitOps 推广

生产推广顺序：

1. 在本地 Kubernetes 固定并验证 KARS。
2. 提交沙箱、身份与策略资源。
3. 按 Digest 固定工作负载镜像和策略包。
4. 在 CI 中运行回归和策略测试。
5. 由应用、平台和安全 Owner 共同评审 Pull Request。
6. 由 Argo CD 或 Flux 协调 AKS。
7. 验证沙箱 Ready 和路由器已加载策略 Digest。
8. 运行部署后的拒绝路径测试。

CI Pipeline 具有四类独立 Gate：

```text
构建 MAF Image
  -> 扫描/签名/固定 Digest
  -> 运行单元测试 + karsEval + Policy 测试
  -> 更新已评审的 karsSandbox Manifest
  -> GitOps 协调到 AKS
  -> Smoke + Denial 测试
```

Forge 可以建议应用修改，却不能更改 Pipeline、批准 Manifest Pull Request 或
创建生产身份。

团队避免命令式修改 GitOps 管理的字段。紧急变更必须立即提交，或明确回滚。

## 多租户边界

当第二个业务部门采用 KARS 时，Ethan 不会把所有 Agent 放入同一共享命名空间。
平台会分离命名空间、Workload Identity、配额、NetworkPolicy、RBAC 和策略
所有权。应用团队不能修改其他租户的治理资源。

## 生产演练

上线前，团队演练：

1. Builder 提交最小 Patch 与通过目标测试的证据。
2. Reviewer 批准拟议 Pull Request。
3. 未 Pairing 的 Agent 提交并被拒绝。
4. 过期 Pairing Token 被拒绝。
5. Builder 尝试批准自己的变更并被拒绝。
6. Reviewer 尝试修改源码并被拒绝。
7. 运维人员从导出证据还原整个工作流。

## 本章结果

Forge 现在是由多个身份协作的系统，而不是两个 Prompt 互相聊天。架构从 Kubernetes
资源到 Runtime 策略与审计，全程保持职责分离。

## 完成定义

当 Artifact 已签名并固定、MAF Production 与 OpenClaw Canary 使用独立 Policy
和身份、GitOps 管理生产字段、Builder 无法自我批准、回滚已经演练，并且部署后
测试证明一条允许路径和一条拒绝路径时，部署才算 Ready。

## 官方参考

- [开始使用](https://github.com/Azure/kars/blob/main/docs/getting-started.md)
- [安全](https://github.com/Azure/kars/blob/main/docs/security.md)
- [使用场景](https://github.com/Azure/kars/blob/main/docs/use-cases.md)
- [功能成熟度](https://github.com/Azure/kars/blob/main/docs/maturity.md)
