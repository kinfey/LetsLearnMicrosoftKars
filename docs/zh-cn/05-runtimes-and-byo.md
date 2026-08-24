# 5. 运行时与自带 Agent

## 运行时 Adapter

KARS 为 OpenClaw、Hermes、OpenAI Agents、Microsoft Agent Framework Python、
LangGraph Python/TypeScript、Anthropic、Pydantic-AI 和自带镜像（BYO）提供
Adapter。

应根据能力而非名称选择：

| 需求 | 起点 |
| --- | --- |
| 完整体验 KARS Mesh/Handoff | OpenClaw 或 Hermes |
| 已有 OpenAI Agents 应用 | OpenAI Agents Adapter |
| 图工作流 | LangGraph Adapter |
| 已有自定义容器 | BYO |

部分运行时名称可能已进入 Schema，但 Adapter 尚未完成。请以当前运行时矩阵为准。

## Adapter 契约

Adapter 将框架特定的模型和工具调用转换为 KARS 路由器契约，从而把提供商凭据和
外部策略留在应用进程之外。

创建自定义镜像之前，先使用上游 Quickstart：

- `examples/openai-agents-quickstart`
- `examples/maf-quickstart`
- `examples/hermes-quickstart`
- `examples/byo-quickstart`

## BYO 要求

自定义镜像必须：

- 以 UID 1000 运行；
- 通过 `127.0.0.1:8443` 的路由器发送外部请求；
- 不包含 Azure 或提供商凭据；
- 遵循已记录的沙箱环境契约；
- 只在运行时允许的位置写入临时数据。

无法直接访问公网是预期行为，不应将其视为需要绕过的网络故障。

## 集成流程

1. 让模型和工具 Endpoint 可配置。
2. 从 Agent 中移除凭据获取逻辑。
3. 以 UID 1000 的非 root 用户运行进程。
4. 构建并扫描镜像。
5. 使用 BYO 运行时部署。
6. 通过路由器审计日志验证推理路径。
7. 测试出口拒绝和预算耗尽。
8. 推广时按 Digest 固定镜像。

KARS 官方镜像已签名并带有供应链元数据，但自动拒绝未签名 BYO 镜像的准入功能
尚未完整实现。生产环境需另行执行镜像策略。

## 练习

改造一个只发送一次模型请求的最小 Agent。先让它使用直接提供商凭据运行，再重构
为镜像不含凭据并使用路由器 Endpoint。比较两种方式的容器环境和网络路径。

## 官方参考

- [运行时 Adapter](https://github.com/Azure/kars/blob/main/docs/runtimes.md)
- [示例](https://github.com/Azure/kars/tree/main/examples)
- [BYO Quickstart](https://github.com/Azure/kars/tree/main/examples/byo-quickstart)
