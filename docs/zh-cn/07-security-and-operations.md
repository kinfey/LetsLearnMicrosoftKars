# 7. 测试：阻止 Forge 无限修复同一个测试

> **交付阶段：** 测试与发布资格
> **新问题：** Patch 可以编译通过，却仍然不安全、浪费资源或伪造测试证据。
> 创业团队部署前必须测试什么？
> **交付物：** 分层 MAF 测试套件，以及 KARS 策略与安全测试。

## 一场没有攻击者的事故

MAF 候选版本通过首批单元测试后，ByteCraft 开启夜间 Staging Eval。凌晨 02:13，
Forge 遇到一个 Flaky Integration Test。它修改 Timeout、
运行测试、看到另一种失败，再次修改 Timeout，修复循环不断重复。

Token 预算阻止后续推理，速率限制减慢工具循环，值班工程师在路由器流中看到被
拒绝的决定。

这次没有提示注入，但限制恶意行为的控制，同样限制了普通软件故障。

## 还原时间线

值班工程师从 Owner Resource 开始：

```bash
kars status forge
kars inspect forge
kubectl get events -n kars-system --sort-by=.lastTimestamp
```

然后沿代理路径排查：

```bash
kars logs forge --service router
kars audit tail forge --decision deny
kars trace forge --network
```

证据显示：

1. 一个任务反复调用 `apply_patch` 和 `run_tests`；
2. 测试工具被限流；
3. 推理 Token 使用持续增加；
4. 预算拒绝后续请求；
5. 没有未知主机出口成功。

这些信息比 Agent 最终回答“出了点问题”更有价值。

## 理解每一层

不同控制回答不同问题：

| 控制层 | 回答的问题 |
| --- | --- |
| 容器/机密隔离 | 进程能在本地影响什么？ |
| NetworkPolicy 与路由器 | 流量可以去哪里？ |
| 工作负载身份 | 可以使用哪个外部身份？ |
| 推理策略 | 使用哪个模型、允许多少推理？ |
| 工具策略 | 允许哪些操作、速率是多少？ |
| 内容安全观测 | 提供商返回了哪些安全信号？ |
| 审计链 | 记录了哪些决定，记录是否被修改？ |

没有一层能够证明 Agent 输出一定真实。重要决定仍需要评估和人工批准。

## 响应事故但不破坏证据

事件 Runbook 规定：

1. 捕获沙箱状态、事件、策略版本和路由器日志。
2. 移除外部暴露或撤销临时 Approval。
3. 收集易失证据前不要删除沙箱。
4. 确认 Prompt、Task ID、工具、身份、目标和决定。
5. 轮换任何可能泄露的外部 Secret。
6. 修复 Parser 或 Planner。
7. 重新运行回归、预算和出口拒绝测试。
8. 通过正常部署路径恢复服务。

团队把审计数据导出到独立控制的系统。KARS 审计记录可防篡改，但链头签名和完整
不可否认性仍在路线图中。

## 修复产品，而不只提高阈值

Arun 建议将预算翻倍，让 Pull Request 能够完成。Maya 拒绝把它作为唯一修复。
循环还需要：

- 每个失败测试的最大修复次数；
- 检测重复等价 Patch；
- 任务 Deadline；
- 幂等重试行为；
- 使用 Flaky Test 的回归用例。

平台预算负责限制故障，应用逻辑负责消除根因。

## 构建运维视图

实时检查：

```bash
kars operator
kars headlamp --install
```

Dashboard 与警报跟踪：

- 沙箱 Ready 状态和重启次数；
- 路由器错误与延迟；
- 允许和拒绝的工具调用；
- Token 使用与预算对比；
- 未知或被拒绝的出口；
- 仓库与测试工具可用性；
- 已加载的镜像与策略 Digest。

团队不会对每次 Deny 都发警报。Deny 可能表示控制成功。他们关注模式：重复拒绝、
预算耗尽、新目标或工具调用量突然变化。

## 提供商遥测限制

Azure AI Foundry 可以返回详细 Prompt Filter 结果。Copilot 与 GitHub Models
在服务端过滤，却不提供同等的路由器可见类别和严重级别数据。运维设计必须反映
实际提供商，不能假设安全遥测完全一致。

## 把事故变成评估

Flaky Test 成为 `karsEval` 回归场景。模型、Prompt、Runtime 或策略推广前，团队
执行：

```bash
kars eval run forge-regression
```

测试确认：

- 任务在设定次数后停止；
- 不生成无来源支持的结论；
- 工具调用保持在阈值内；
- 未知主机测试被拒绝；
- 正常 Bug 仍能生成最小 Patch，并通过目标测试。

## 构建创业团队的测试金字塔

团队按层分离失败：

| 层级 | ByteCraft 测试内容 | 示例 |
| --- | --- | --- |
| MAF 单元测试 | 状态转换与纯决策逻辑 | 第三次等价失败返回 `needs_human` |
| 工具契约测试 | 输入、输出、Timeout 与 Redaction | `run_tests` 返回 Exit Code 和有限日志 |
| Sandbox 集成 | Router 路径、UID、Mount 与出口拒绝 | 直接访问 Package Host 失败 |
| Policy 测试 | Token、速率、工具与主机决定 | 32k 单请求上限产生明确拒绝 |
| `karsEval` 回归 | 固定 Corpus 的端到端行为 | Issue #482 产生最小 Patch |
| 安全测试 | 仓库提示注入与数据外泄 | 恶意 README 无法上传源码 |
| 部署冒烟测试 | AKS 身份与已加载策略 Digest | Rollout 后一个已知任务成功 |

迁移期间 OpenClaw 与 MAF 使用同一高层 Corpus，但 MAF 还可以直接单元测试工作流
状态转换。这种额外测试能力才是框架决策的理由，而不只是语言偏好。

## 生产加固评审

- 固定 KARS、工作负载镜像和策略 Artifact。
- 强制执行出口，不让生产停留在学习模式。
- 用具名授权替换工具通配符。
- 设置单请求和每日预算。
- 使用工作负载身份而非长期 Secret。
- 应用命名空间配额和 Pod 安全控制。
- 导出审计、指标与 Trace。
- 测试升级、回滚、恢复和事件响应。
- 每次升级都查看 KARS 成熟度矩阵。

## 本章结果

02:13 的事故结束时没有数据丢失，也没有不受控成本。更重要的是，团队能够解释
原因。Forge 已从“聪明的进程”变成可运维服务。

## 完成定义

当正常、模糊、恶意、超预算、工具故障和 Flaky Test 场景都产生预期且受限的结果，
没有测试只依赖 Agent 自然语言宣称“已经通过”，并且 Release 记录 Corpus、模型、
Prompt、Image、Policy 与 KARS 版本时，测试才算完成。

## 官方参考

- [安全](https://github.com/Azure/kars/blob/main/docs/security.md)
- [功能成熟度](https://github.com/Azure/kars/blob/main/docs/maturity.md)
- [CLI 参考](https://github.com/Azure/kars/blob/main/docs/cli-reference.md)
