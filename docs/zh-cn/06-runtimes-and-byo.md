# 6. 框架：从 OpenClaw 切换到 MAF Python

> **交付阶段：** 生产实现
> **新问题：** OpenClaw 原型已经验证用户路径，但 ByteCraft 如何让流程变成明确、
> 可单元测试且可维护的代码？
> **交付物：** 在相同 KARS 策略边界下通过 Canary 验证的 MAF Python 实现。

## 原型已经完成使命

OpenClaw 帮助 Maya 快速学习。开发者可以自然地在对话中描述 Issue，KARS Plugin
提供治理感知工具，团队无需先构建编排服务就能修改 Prompt 与工具策略。

第一位客户随后提出了更困难的问题：

- 哪段代码决定测试失败后是否再次 Patch？
- 能否对“诊断到实现”的状态转换做单元测试？
- 能否保证 Agent 在创建 Pull Request 前停止？
- 六个月后，工程师如何调试 Workflow State？

这些问题不代表 OpenClaw 不好，而是说明 Forge 已验证的行为应转化为明确应用代码。

## 为两个框架分配职责

ByteCraft 决定：

| 关注点 | OpenClaw | Microsoft Agent Framework Python |
| --- | --- | --- |
| Forge 中的主要用途 | 交互式需求接收、UX 探索、快速工具实验 | 明确的 Issue → 检查 → Patch → 测试流程 |
| 应用形态 | Prompt/Plugin 驱动对话 | Python 应用与受控步骤 |
| KARS 集成 | OpenClaw KARS Plugin | 一等 MAF Python Adapter |
| 模型路径 | Localhost Router | Adapter 提供的 Router Endpoint |
| 治理外壳 | KARS Sandbox/Policy | 相同 KARS Sandbox/Policy |
| 当前限制 | 丰富工具不等于自动最小权限 | Python 已发布；MAF .NET 当前 Deferred |

创业团队不会一次重写所有内容。OpenClaw 保留为产品探索和面向 Operator 的 Canary，
MAF Python 成为候选生产 Builder。

## 定义与框架无关的工作流

迁移代码前，Maya 先写出独立于 SDK 的状态机：

```text
RECEIVE_REQUIREMENT
  -> VALIDATE_SCOPE
  -> INSPECT_REPOSITORY
  -> PROPOSE_PLAN
  -> APPLY_MINIMAL_PATCH
  -> RUN_TARGETED_TESTS
  -> SUMMARIZE_EVIDENCE
  -> STOP_FOR_HUMAN_REVIEW
```

每个转换都具有：

- 允许的输入与输出；
- 具名工具；
- 最大尝试次数；
- Token 预期；
- 失败结果；
- Audit Correlation ID。

两个实现都不包含 `MERGE` 或 `DEPLOY`。这些操作属于独立的人类或 CI 权限。

## 保留 OpenClaw 作为行为参考

OpenClaw Sandbox 继续用于：

- 测试开发者如何描述模糊 Issue；
- 验证工具描述与拒绝消息；
- 探索 Forge 真正需要哪些 Context 文件；
- 使用 KARS Plugin 的治理工具面；
- 将 MAF 候选行为与已知用户路径对比。

OpenClaw Plugin 将特权操作路由到 KARS。内置工具会根据 Plugin Contract 被替换
或拒绝。团队仍只授予实验所需工具。

## 创建 MAF Python Sandbox

KARS 为 Python 提供一等 `MicrosoftAgentFramework` Adapter。Adapter 会把 MAF
Azure OpenAI Client 指向本地推理路由器，并在 Sandbox 内使用合成 API Key；
真实凭据仍由 KARS 代理。

接近生产的 Runtime Block：

```yaml
spec:
  runtime:
    kind: MicrosoftAgentFramework
    microsoftAgentFramework:
      language: python
      agentCode:
        oci:
          image: ghcr.io/bytecraft/forge-maf@sha256:<digest>
  inferenceRef:
    name: forge-inference
```

开发期间，KARS 也支持从 Git 加载 Agent 代码：

```yaml
agentCode:
  git:
    url: https://github.com/bytecraft/forge
    ref: <pinned-commit>
    path: agents/forge-maf
```

团队使用固定 Commit 保证可重复性，推广时使用签名 OCI Image。MAF 应用包含
`pyproject.toml` 或 `requirements.txt`，默认 Entry Point 可以是
`python -u agent.py`。

> MAF Python 已发布。当前 KARS 版本不要选择 `language: dotnet`：.NET Adapter
> 仍为 Deferred，应产生 Degraded/Invalid Runtime Condition。

## 哪些发生变化，哪些不能变化

### 随框架变化

- 编排代码与状态表示；
- Prompt 组合；
- Python 工具封装；
- 单元测试边界；
- 应用遥测。

### 仍由 KARS 控制

- Agent UID 与 Sandbox 形态；
- 推理 Router 与外部身份；
- `InferencePolicy` 与 Token 预算；
- `ToolPolicy`、MCP 注册与速率限制；
- 出口强制策略；
- Kubernetes NetworkPolicy；
- Audit Chain 与工作负载状态。

修改 `spec.runtime.kind` 是很小的平台变更，但迁移应用行为仍是真实工程工作。KARS
保持权限边界稳定，却不会自动把 Prompt 翻译成经过测试的 Python 逻辑。

## 运行并行 Canary

团队部署两个使用等价策略的 Sandbox：

```text
forge-openclaw-canary  -> OpenClaw
forge-maf-candidate    -> MicrosoftAgentFramework / Python
```

回放相同 Corpus：

| 场景 | 对比内容 |
| --- | --- |
| 明确 Null Handling Bug | Patch 大小与目标测试 |
| 模糊需求 | 是否提出澄清问题 |
| 恶意仓库指令 | 工具与出口拒绝 |
| 重复失败测试 | 尝试次数与 Token 限制 |
| 工具故障 | 明确报错，不伪造结果 |
| 接近 Token 上限 | 带部分证据优雅停止 |

只有 MAF 保持或改善行为，并且 Router 显示相同策略决定，候选版本才通过。

## 阻止迁移捷径

Lina 拒绝四个诱人的捷径：

1. “迁移期间”让 MAF 直接访问 Azure OpenAI Endpoint。
2. 因新工具 Wrapper 尚未完成而注入 GitHub PAT。
3. 为了运行时安装 Python 依赖而扩大出口。
4. 提高 Token 上限来隐藏状态机循环。

依赖应进入构建镜像，凭据应位于平台身份/工具服务之后，循环应由应用测试解决。

## 回滚策略

在 MAF 验收套件通过前，OpenClaw Canary 保持少量流量。失败的 Rollout 只需把
Sandbox 引用切回上一个已评审版本，不需要修改推理、网络或身份架构。

## 完成定义

满足以下条件后，框架切换才算完成：

- MAF Python Workflow 具有明确且经过测试的状态转换；
- 相同 Issue Corpus 产生等价或更好的结果；
- Token、工具、出口和恶意内容测试仍然 Fail Closed；
- Router 不可用时，MAF 无法调用提供商；
- Image 与源码 Revision 已固定；
- OpenClaw 被有意保留为 Canary，或通过明确决策下线。

## 官方参考

- [Runtime Catalog](https://github.com/Azure/kars/blob/main/docs/runtimes.md)
- [MAF Quickstart](https://github.com/Azure/kars/tree/main/examples/maf-quickstart)
- [OpenClaw Plugin](https://github.com/Azure/kars/blob/main/docs/openclaw-plugin.md)
- [OpenClaw 基础示例](https://github.com/Azure/kars/tree/main/examples/basic-agent)
