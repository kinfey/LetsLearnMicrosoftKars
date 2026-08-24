# 1. 为什么需要 KARS？

## 学习目标

完成本章后，你将能够解释直接向 Agent 提供凭据和网络访问的风险、描述 KARS
的数据路径，并为不同场景选择合适的部署模式。

## Agent 基础设施问题

AI Agent 不只是生成文本。它可以调用工具、读取数据、发起网络请求，并代表用户
执行操作。因此，提示注入或错误规划可能演变为真实的基础设施事故。

传统应用控制必不可少，但并不足够。如果 Agent 进程同时拥有云凭据和不受限制的
网络出口，那么解释不可信内容的进程本身也掌握了安全边界。

KARS（Agent Reference Stack for Kubernetes）采用了不同的核心原则：

> Agent 不拥有访问外部服务或 Azure 凭据的独立路径。

每个 Agent 都运行在 Kubernetes 沙箱中，并配有专属推理路由器。路由器代理推理、
身份、工具调用、内容安全观测、预算、网络出口和审计事件。Kubernetes 隔离与
NetworkPolicy 使路由器成为预期的外部数据通道。

## 核心组件

| 组件 | 职责 |
| --- | --- |
| KARS Controller | 将自定义资源协调为 Pod、Service、策略和身份资源 |
| Agent 容器 | 以 UID 1000 运行所选框架或自定义 Agent |
| 推理路由器 | 代理外部访问并执行策略 |
| Egress Guard | 建立沙箱网络路径 |
| A2A Gateway/Core | 处理 Agent 间暴露与路由 |
| KARS CLI | 封装本地、Kubernetes、Azure、Helm 和运维流程 |

工作负载的基本单元是 `KarsSandbox`，策略资源则描述该沙箱可以推理、调用和访问
哪些内容。

## 三种部署形态

### 本地 Docker

`kars dev --release` 将 Agent 和路由器放在同一个容器中。它适合快速冒烟测试，
但无法复现生产环境中的容器边界和 NetworkPolicy。

### 本地 Kubernetes

`kars dev --release --target local-k8s` 创建 kind 集群，并部署接近生产形态的
多容器 Pod。这是推荐的学习模式。

### AKS

`kars up` 提供托管 Kubernetes 路径、Azure 身份选项以及可选的机密隔离。请先在
本地验证工作负载，再进入此阶段。

## 项目状态

KARS 是开源、自托管的 alpha 软件。其 API 使用 `kars.azure.com/v1alpha1`，
小版本之间也可能出现破坏性变化。它是参考实现，而不是托管服务，也不提供
Microsoft 产品 SLA。部分高级信任、A2A 验证、证明和供应链准入功能仍不完整。

本教程示例固定到 `v0.1.25`。请以上游源码、CRD Schema 和
`kars <command> --help` 为准。

## 检查点

如果你能回答以下问题，就可以继续：

1. 为什么 Agent 进程不应持有外部凭据？
2. 哪个组件负责执行推理和出口策略？
3. 为什么本地 Kubernetes 比本地 Docker 更接近生产？

## 官方参考

- [README](https://github.com/Azure/kars/blob/main/README.md)
- [架构](https://github.com/Azure/kars/blob/main/docs/architecture.md)
- [成熟度](https://github.com/Azure/kars/blob/main/docs/maturity.md)
- [安全](https://github.com/Azure/kars/blob/main/docs/security.md)
