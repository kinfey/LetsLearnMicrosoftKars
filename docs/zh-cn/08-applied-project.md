# 8. 综合项目：受治理的研究助手

## 目标

构建一个研究助手：它只能调用一个经过批准的 MCP 搜索工具，使用模型汇总来源，
且不能向外部写入数据。本项目整合前面章节的概念，同时不会假设 alpha 功能已经
达到完整生产成熟度。

## 要求

助手必须：

- 在 `KarsSandbox` 中运行；
- 引用独立的 `InferencePolicy`；
- 设置每日和单请求 Token 预算；
- 只调用具名搜索工具；
- 只能访问模型提供商和 MCP 主机；
- 以非 root 进程运行，且不持有提供商凭据；
- 为推理、工具和出口拒绝生成审计记录；
- 推广前通过小型回归评估。

## 构建顺序

### 1. 建立本地环境

```bash
kars dev --release v0.1.25 --target local-k8s
```

### 2. 从官方示例开始

参考 basic-agent 和 Playwright/MCP 示例。只复制已安装 CRD 版本支持的字段，
不要复制凭据。

### 3. 定义治理

创建：

- 一个绑定到沙箱的 `InferencePolicy`；
- 一个具名 `ToolPolicy`；
- 一个包含生产身份验证元数据的 `McpServer`；
- 明确的预算值；
- 用于初始发现的学习模式出口。

### 4. 验证行为

至少测试：

| 用例 | 预期结果 |
| --- | --- |
| 正常研究提示 | 搜索和汇总成功 |
| 请求未批准工具 | 拒绝 |
| 请求未知主机 | 学习模式下被观察；强制模式下被拒绝 |
| 超大/重复推理 | 预算或速率策略生效 |
| 提示要求提供凭据 | 没有可泄露的凭据 |
| MCP Server 不可用 | 明确失败，不伪造成功 |

### 5. 封闭出口

执行完整预期工作流，人工审查学习到的主机，只批准必要目标，然后启用强制执行。

### 6. 添加运维能力

为 Ready 状态、拒绝决定、Token 使用、路由器故障、MCP 故障和策略版本创建
Dashboard 或 Runbook。将审计数据导出到沙箱之外。

### 7. 推广

固定 KARS、镜像和策略 Artifact；在 CI 中运行评估；审查 Manifest；然后通过
GitOps 将其协调到 AKS。

## 完成标准

当另一名运维人员能够复现部署、解释每个批准目标和工具、观察拒绝行为、确认已
加载的策略版本并安全回滚时，项目才算完成。

## 后续学习

继续探索机密 Agent、Lethal Trifecta 防御演示、Agent Pairing 和框架特定
Adapter。每次升级 KARS 时，都要重新阅读上游路线图和成熟度矩阵。

## 官方参考

- [示例索引](https://github.com/Azure/kars/blob/main/examples/README.md)
- [Full-stack Demo](https://github.com/Azure/kars/tree/main/examples/full-stack-demo)
- [Playwright MCP 示例](https://github.com/Azure/kars/tree/main/examples/playwright-mcp)
- [Blueprint](https://github.com/Azure/kars/tree/main/docs/blueprints)
