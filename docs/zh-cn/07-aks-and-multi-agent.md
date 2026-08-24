# 7. AKS、身份与多 Agent 系统

## 迁移到 AKS

前置条件包括 Azure CLI、Helm 3.14 或更高版本、Azure 订阅，以及创建所需资源
的权限。

```bash
az login
az account set --subscription <subscription-id>
kars up \
  --name prod-agent \
  --region swedencentral \
  --release v0.1.25
```

默认 Mesh 层使用集群工作负载身份和匿名 Mesh 注册。若要使用每沙箱 Entra Agent
ID 和已验证 Mesh 身份：

```bash
kars up \
  --name prod-agent \
  --region swedencentral \
  --release v0.1.25 \
  --mesh-trust=entra
```

Entra 路径需要额外租户权限。选择区域前，应同时确认模型、AKS、身份、配额和
机密计算的可用性。

## 多 Agent 控制

KARS 提供 Mesh、Pairing、Handoff 和 A2A 功能：

```bash
kars mesh setup-trust
kars mesh status
kars pair generate --expires 30d --token-budget 100000
kars a2a list-exposed
kars handoff prod-agent --to cloud
```

Pairing 必须限制有效期和预算。Agent 间可连接并不代表可信：需要验证 Peer 身份、
授权所请求的操作，并限制释放的数据。

基于 Signal 的加密 Mesh Session 使消息内容对 Relay 保持不透明，但部分
TrustGraph 和 A2A 验证路径仍不完整。用于生产前请查看成熟度文档。

## 机密与多租户工作负载

当威胁模型要求 Kata/SEV-SNP 支持的执行环境时，可使用机密沙箱隔离。它需要额外
基础设施，但不能取代应用、身份或出口策略。

对于多租户，应分离命名空间和身份，应用配额与网络策略，并防止某个应用团队修改
其他租户的治理资源。

## GitOps 推广

1. 在本地 Kubernetes 验证固定版本。
2. 提交沙箱和策略 Manifest。
3. 按 Digest 引用镜像和策略包。
4. 在 CI 中运行评估和策略测试。
5. 通过 Pull Request 推广。
6. 由 Argo CD 或 Flux 协调 AKS。
7. 观察 Ready 状态和路由器已加载的策略 Digest。

## 练习

设计两个 Agent：研究员和审批员。说明身份、允许工具、出口、Token 预算、
Pairing 有效期、两者之间传递的数据，以及审批所需的审计证据。

## 官方参考

- [开始使用](https://github.com/Azure/kars/blob/main/docs/getting-started.md)
- [安全](https://github.com/Azure/kars/blob/main/docs/security.md)
- [使用场景](https://github.com/Azure/kars/blob/main/docs/use-cases.md)
- [成熟度](https://github.com/Azure/kars/blob/main/docs/maturity.md)
