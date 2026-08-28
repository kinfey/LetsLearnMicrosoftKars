# 2. 原型：用 OpenClaw 构建第一条垂直链路

> **交付阶段：** 原型
> **新问题：** 创业团队能否在一天内验证 Issue 到 Patch 的用户路径？
> **Runtime 重点：** OpenClaw，因为其 Plugin 与工具面适合快速对话式迭代。

## 周一早晨

Maya 想立刻把 Forge 连接到客户的生产 Monorepo，但 Ethan 阻止了她。

“首先要有可重复的环境。如果本地看不到路由器、Pod 和策略边界，我们就会同时
调试应用和平台。”

团队为本章设定了一个明确结果：启动 KARS 沙箱、检查真实 Kubernetes 形态、
发送一次请求，并完整清理环境。

## 准备工作站

推荐学习路径使用本地 Kubernetes。在 macOS 或 Linux 上检查：

```bash
node --version              # Node.js 22+
docker version              # 或兼容的容器引擎
kind version
kubectl version --client
```

团队还需要一种推理服务：

- 带有效席位和设备登录的 GitHub Copilot；
- 带 Endpoint、Deployment 和凭据的 Azure AI Foundry/Azure OpenAI；
- 带 `models:read` 权限的 GitHub Models Token。

第一次本地运行选择 Copilot，因为无需把 Azure 服务凭据放入实验环境。

原型阶段选择 KARS 默认的 **OpenClaw** Runtime。OpenClaw 的 KARS Plugin 提供
治理感知工具，适合观察开发者如何描述任务。这是产品学习选择，并不代表生产实现
必须一直使用 OpenClaw。

## 安装已知版本的 CLI

```bash
npm install --global @kars-runtime/cli
kars --version
kars dev --help
```

Maya 在实验记录中同时写下教程版本和安装版本。KARS 仍处于 alpha，参数可能变化。

## 创建本地 Kubernetes 环境

```bash
kars dev --release v0.1.25 --target local-k8s
```

该命令创建 kind 集群、安装 KARS 组件并启动开发沙箱。Maya 按提示完成提供商
身份验证。

Ethan 没有让她立即连接，而是先检查创建结果：

```bash
kubectl get namespaces
kubectl get pods -n kars-system
kubectl get networkpolicy -n kars-system
kars list
kars status dev-agent
kars inspect dev-agent
```

他们寻找三个事实：

1. 沙箱达到 `Ready`。
2. Agent 与路由器在 Kubernetes Pod 形态中作为不同容器运行。
3. NetworkPolicy 确实存在；路由器不是 Forge 引入的普通代码库。

## 跟踪第一次对话

现在 Maya 执行：

```bash
kars connect dev-agent
```

她输入：

```text
你是 Forge 研发 Agent。请解释为什么读取不可信仓库内容的 Agent 不应持有
GitHub 或模型凭据。不要调用任何工具。
```

接着，她为 Forge 提供一个一次性仓库和小型 Issue：

```text
add_note 函数在 note 为 null 时崩溃。只检查分配的 Workspace，
提出最小 Patch，并说明应运行哪个目标测试。不要 Merge，也不要访问外部主机。
```

这条垂直链路有意保持不完整：对话、代码检查、Patch 建议和一个测试建议。创建 PR
和 Merge 仍在原型边界之外。

请求运行时，Ethan 观察路由器：

```bash
kars logs dev-agent --service router -f
```

真正重要的不是模型生成了哪段文字，而是用户请求、Agent 容器、路由器事件和模型
响应之间的关系。

## 主动破坏实验

Lina 要求 Maya 在习惯成功路径之前先测试失败。

他们停止提供商身份验证，或临时使用无效 Deployment。预期结果应是可见的
401/403 或提供商错误，而不是伪造答案或无限重试。

随后检查：

```bash
kars status dev-agent
kars logs dev-agent --service router
kubectl get events -n kars-system --sort-by=.lastTimestamp
```

团队采用以下排查顺序：

| 现象 | 首先检查的证据 |
| --- | --- |
| 找不到 `kars` | npm 全局二进制目录与 `PATH` |
| kind 集群失败 | 容器引擎是否可用 |
| Pod 持续 Pending | Kubernetes 事件与调度消息 |
| 沙箱 Degraded | `karsSandbox.status.conditions` |
| 推理返回 401/403 | 提供商身份、Endpoint 与 Deployment |
| 路由器不可用 | 路由器容器日志与 Readiness |
| 文档参数失败 | 安装版本与命令级 Help |

该顺序可以避免在真正问题是身份或协调时错误修改应用代码。

## 与 Docker 模式对比

为了快速比较，他们还执行：

```bash
kars dev down
kars dev --release v0.1.25
```

响应看起来相似，但部署不具备同等容器隔离或 Kubernetes NetworkPolicy。Maya
在测试报告中写道：

> Docker 模式证明研发 Prompt 可以启动，但不能证明源码或生产隔离。

后续课程继续使用本地 Kubernetes。

## 明确清理环境

```bash
kars dev down
```

如果清理报错，应先检查 kind 集群和 KARS 状态，再手工删除。可重复创建和清理是
产品能力的一部分，不只是杂务。

## 实验交付物

创建一张简短证据表：

| 证据 | 命令 | 证明内容 |
| --- | --- | --- |
| 沙箱条件 | `kars status dev-agent` | Controller 协调结果 |
| Pod 容器 | `kubectl get/describe pod` | Agent/路由器部署形态 |
| NetworkPolicy | `kubectl get networkpolicy` | Kubernetes 网络控制存在 |
| 路由器事件 | `kars logs ... --service router` | 推理经过代理路径 |
| 失败输出 | 无效提供商测试 | 错误明确且可观察 |

下一章会打开自动生成的 Sandbox，逐一测试隔离边界，然后再把它表达为可在 Git
中评审的资源。

## 完成定义

当开发者能够提交一个受限 Issue、通过 Router 观察 OpenClaw 请求、收到最小 Patch
建议，并在移除提供商身份后看到明确失败时，原型才算完成。

## 官方参考

- [快速入门](https://github.com/Azure/kars/blob/main/docs/quickstart.md)
- [开始使用](https://github.com/Azure/kars/blob/main/docs/getting-started.md)
- [CLI 参考](https://github.com/Azure/kars/blob/main/docs/cli-reference.md)
