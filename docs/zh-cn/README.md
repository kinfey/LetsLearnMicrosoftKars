# 一起学习 Microsoft KARS

本教程共八章，从 KARS 的安全模型逐步讲到面向生产的综合应用。如果你刚接触
KARS 或 Kubernetes Agent 基础设施，建议按顺序学习。

## 目录

1. [为什么需要 KARS？](01-why-kars.md)
2. [本地快速入门](02-local-quickstart.md)
3. [Kubernetes API 与核心概念](03-kubernetes-api.md)
4. [推理、工具、MCP 与出口策略](04-policies-and-tools.md)
5. [运行时与自带 Agent](05-runtimes-and-byo.md)
6. [安全、可观测性与运维](06-security-and-operations.md)
7. [AKS、身份与多 Agent 系统](07-aks-and-multi-agent.md)
8. [综合项目：受治理的研究助手](08-applied-project.md)

## 约定

- 命令使用兼容 POSIX 的 Shell。
- 请替换 `<尖括号>` 中的值。
- 示例使用 `kars-system` 命名空间。
- 默认学习环境为本地 Kubernetes。
- 生产建议以 AKS 为基础。

[English edition](../en/README.md)
