# 一起学习 Microsoft KARS

本教程以九章连续故事跟随四人创业团队 **ByteCraft AI**：他们必须在不赌上公司
现金流和首位客户源码安全的前提下，发布从 Issue 到 Pull Request 的研发 Agent
Forge。每章从一个新的交付问题开始，以工程决策或可验证产物结束。

团队有意识地采用两个框架：

- 使用 **OpenClaw** 快速完成对话式原型和工具迭代。
- 当流程需要成为明确、可测试的应用代码时，切换到
  **Microsoft Agent Framework（MAF）Python**。

应用框架发生变化时，KARS 仍保持一致的 Sandbox、Router、Policy、Audit 和网络
控制。

## 目录

1. [需求：演示之前先约束产品](01-why-kars.md)
2. [原型：用 OpenClaw 构建第一条垂直链路](02-local-quickstart.md)
3. [开发：保护客户代码仓库](03-inside-the-sandbox.md)
4. [平台：把演示变成 Kubernetes 契约](04-kubernetes-api.md)
5. [治理：控制 Token、工具和出口](05-policies-and-tools.md)
6. [框架：从 OpenClaw 切换到 MAF Python](06-runtimes-and-byo.md)
7. [测试：阻止 Forge 无限修复同一个测试](07-security-and-operations.md)
8. [部署：把 Forge 推广到 AKS](08-aks-and-multi-agent.md)
9. [发布：交付 Issue 到 PR 的完整流程](09-applied-project.md)

## 创业团队

| 成员 | 创业团队角色 | 核心关注 |
| --- | --- | --- |
| Maya | 联合创始人兼 AI 工程师 | 交付有用的 Agent 行为 |
| Arun | 产品负责人 | 解决客户的研发瓶颈 |
| Ethan | 平台工程师 | 让环境可重复、可运维 |
| Lina | 安全工程师 | 限制源码、身份、工具、成本与出口 |

## 约定

- 命令使用兼容 POSIX 的 Shell。
- 请替换 `<尖括号>` 中的值。
- 示例使用 `kars-system` 命名空间。
- 默认学习环境为本地 Kubernetes。
- 生产建议以 AKS 为基础。

[English edition](../en/README.md)
