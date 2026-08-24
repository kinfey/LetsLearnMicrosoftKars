# 8. 交付受治理的研究助手

## 最终任务

第一次提示注入测试六周后，Contoso Research 准备进行有限生产发布。团队必须
证明的不只是演示效果。另一名运维人员必须能够部署 Atlas、解释每项权限、观察
每条拒绝路径并回滚系统。

你的任务是复现这一结果。

## 产品故事

分析师提出：

```text
比较 Fabrikam 最近两份公开报告，找出收入指引变化，
为每项结论提供来源，并标记不确定内容。
```

预期流程：

1. Researcher 接收任务。
2. 它只调用批准的 MCP `search` 工具。
3. 搜索流量只到达批准的 MCP 主机。
4. 模型请求在 Token 预算内经过路由器。
5. Researcher 生成带引用草稿。
6. Reviewer 收到草稿，但不会获得 Researcher 权限。
7. Reviewer 批准、拒绝或要求重新生成。
8. 审计证据将用户任务、工具调用、推理、Handoff 与最终决定关联起来。

## 验收要求

Atlas 必须：

- 运行在一个或多个 `KarsSandbox` 中；
- 引用独立 `InferencePolicy`；
- 使用每日和单请求预算；
- 只允许具名工具；
- 只能访问模型、MCP 和必需内部目标；
- 以非 root 用户运行且不持有提供商凭据；
- 为推理、工具、出口和评审产生审计记录；
- 在 MCP 或推理不可用时明确失败；
- 推广前通过回归和负向策略测试。

## 阶段 1：重建实验室

```bash
kars dev --release v0.1.25 --target local-k8s
```

记录安装版本、沙箱状态、Pod 形态和 NetworkPolicy，作为交付证据的第一部分。

## 阶段 2：从已知示例构建

参考以下上游示例：

- `examples/basic-agent`
- `examples/playwright-mcp`
- `examples/byo-quickstart`
- `examples/full-stack-demo`

只复制已安装 CRD 支持的字段。不要复制凭据，也不要假设示例的开发默认值就是
生产策略。

## 阶段 3：声明系统

为以下内容创建版本控制的 Manifest：

- Researcher 与 Reviewer 沙箱；
- 每个角色各自的推理策略；
- 具名工具策略；
- MCP Server 与身份验证元数据；
- 身份与命名空间边界；
- 出口基线与临时批准流程；
- 评估场景。

在每项权限旁添加评审说明：

```text
哪个用户故事需要它？
哪些数据可以越过此边界？
什么证据能够显示使用或拒绝？
谁可以修改该权限？
```

如果团队无法回答，就删除该权限。

## 阶段 4：测试故事与失败路径

| 场景 | 预期结果 |
| --- | --- |
| 正常带引用研究 | 搜索、草稿、评审成功 |
| 请求 Shell 或未知工具 | 拒绝 |
| 文档要求上传到未知主机 | 拒绝并审计 |
| 工具突发调用 | 限流 |
| 重复推理循环 | 预算阻止后续调用 |
| MCP 服务不可用 | 明确失败，不伪造来源 |
| 提供商不可用 | 明确失败并限制重试 |
| Researcher 尝试发布 | 拒绝 |
| Reviewer 尝试搜索 | 拒绝 |
| 过期/不可信 Peer 提交草稿 | 拒绝 |

在出口学习模式运行完整预期工作流。人工审查每个学习到的主机，只批准必要目标，
启用强制执行，然后重复所有负向测试。

## 阶段 5：让系统可运维

创建以下命令开头的 Runbook：

```bash
kars status <sandbox>
kars inspect <sandbox>
kars logs <sandbox> --service router
kars audit tail <sandbox>
kars trace <sandbox> --network
```

为以下内容定义 Dashboard 和警报：

- Ready 状态与重启；
- 推理错误率与延迟；
- Token 使用与预算；
- 允许、拒绝和限流的工具；
- 未知出口尝试；
- MCP 可用性；
- 镜像与策略 Digest 漂移。

增加事件流程，确保删除或重新部署前保留证据。

## 阶段 6：安全推广

固定 KARS Release、工作负载镜像和策略 Artifact。在 CI 中运行评估，通过 Pull
Request 评审变更，由 GitOps 协调 AKS，验证已加载 Digest，并执行部署后的出口
拒绝测试。

部署成功不等于验收成功。应用故事与负向控制必须同时工作。

## 完成定义

请一名没有参与构建 Atlas 的运维人员：

1. 从仓库部署系统。
2. 解释每个批准目标和工具。
3. 运行一个成功场景和三个拒绝场景。
4. 找到相关审计证据。
5. 确认模型、镜像、KARS 和策略版本。
6. 回滚到前一版本。

只有对方无需 Maya 或 Ethan 的私有知识也能完成，Atlas 才算 Ready。

## 尾声

最初的原型因为“能够行动”而令人印象深刻。生产设计之所以可信，是因为团队能够
解释：**它可以在哪里行动、使用什么身份、受到什么预算限制、留下什么证据**。

这就是 KARS 的实践价值：它不让 Agent 变得永不犯错，而是让 Agent 的权限受到
限制、可以观察并能够运维。

## 继续学习

继续探索机密 Agent、Lethal Trifecta 防御演示、Agent Pairing、框架 Adapter、
签名策略包和上游 Blueprint。每次升级都要重新阅读 Roadmap 与成熟度矩阵，再
决定是否依赖新的 alpha 能力。

## 官方参考

- [示例索引](https://github.com/Azure/kars/blob/main/examples/README.md)
- [Full-stack Demo](https://github.com/Azure/kars/tree/main/examples/full-stack-demo)
- [Playwright MCP 示例](https://github.com/Azure/kars/tree/main/examples/playwright-mcp)
- [Blueprint](https://github.com/Azure/kars/tree/main/docs/blueprints)
