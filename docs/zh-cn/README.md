# 一起学习 Microsoft KARS

本教程以一条连续故事贯穿八章：Contoso Research 团队把权限过大的 Atlas 原型，
逐步改造成受治理的研究助手。每章都从产品决定、故障或动手排查引入 KARS。

## 目录

1. [一封改变架构的邮件](01-why-kars.md)
2. [在安全的本地实验室复现 Atlas](02-local-quickstart.md)
3. [把演示变成 Kubernetes 契约](03-kubernetes-api.md)
4. [赋予 Atlas 有用但受限的能力](04-policies-and-tools.md)
5. [把 Atlas 迁入受治理的 Runtime](05-runtimes-and-byo.md)
6. [Atlas 开始循环的那个夜晚](06-security-and-operations.md)
7. [从一个沙箱到生产团队](07-aks-and-multi-agent.md)
8. [交付受治理的研究助手](08-applied-project.md)

## 约定

- 命令使用兼容 POSIX 的 Shell。
- 请替换 `<尖括号>` 中的值。
- 示例使用 `kars-system` 命名空间。
- 默认学习环境为本地 Kubernetes。
- 生产建议以 AKS 为基础。

[English edition](../en/README.md)
