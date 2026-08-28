# 3. 开发：保护客户代码仓库

> **交付阶段：** 开发环境
> **新问题：** Forge 如何执行客户代码，却看不到无关源码、开发者凭据或不受限制
> 的网络？
> **交付物：** 经过测试的 Sandbox 边界与一次性 Workspace 设计。

## “Sandbox”背后的问题

ByteCraft 的 Design Partner 愿意提供一个小型私有仓库，但前提是团队解释源码
存放位置和访问主体。完成本地实验后，Maya 说：“Forge 现在已经运行在 Sandbox
中。”

Lina 提出了一个看似简单的问题：

> Sandbox 到底保护什么，又不保护什么？

Sandbox 不是一个有魔力的标签。对 Forge 而言，它必须保护私有源码、隔离 Agent
与凭据、限制网络目标，并留下足够证据来解释失败或恶意操作。如果团队说不清这些
边界，就无法测试它们。

本章暂停功能开发，逐层打开 Sandbox。

## `karsSandbox` 是工作单元

在 KARS 中，一个 `karsSandbox` 代表一个 Agent 工作负载。它连接：

- OpenClaw、Hermes、其他 Adapter 或 BYO Runtime；
- 必需的 `InferencePolicy`；
- Sandbox 隔离与安全设置；
- 网络策略和可选 Approval；
- 自动生成的 Kubernetes 资源；
- 协调状态与 Conditions。

自定义资源是期望状态契约，运行中的 Pod 是该契约产生的结果之一。直接修改 Pod
不会重新定义 Sandbox；Controller 可能在协调期间替换它。

在 Forge 故事中，一个 Sandbox 表示一个研发角色的一次受限执行上下文。这不代表
所有开发者、仓库和 Agent 都应该共享一个长期 Workspace。

## 打开接近生产形态的 Pod

在本地 Kubernetes 与 AKS 中，关键 Pod 形态如下：

```text
karsSandbox: forge
└── Pod
    ├── init: egress-guard
    ├── agent             UID 1000
    └── inference-router  UID 1001
```

### `egress-guard`

Init Container 安装网络规则，使 Agent UID 可以通过 Loopback 到达路由器，却无法
建立独立外部路径。它是 Safety Net，而不是策略决策点。

### `agent`

Forge 与 Runtime 以 UID 1000 运行。Agent 可以读取分配的 Workspace 并调用本地
路由器，但不应持有提供商凭据或直接出口。

### `inference-router`

Rust 路由器以 UID 1001 运行。面向模型的 HTTP Endpoint 使用端口 `8443`，
Forward Proxy 路径使用 `8444`。它负责评估策略、预算、身份、出口、治理和审计。

UID 分离十分重要：Forge 解释或执行的代码，不会以持有外部权限的路由器用户运行。

## 围绕一次代码修改的五层边界

Maya 给 Forge 分配包含 Issue #482 的 Workspace。团队沿任务检查五层边界。

### 1. 进程边界

Forge 以非 root Agent 进程运行，路由器使用不同 UID。研发 Agent 执行的命令
不应读取路由器的进程环境或凭据材料。

本地 Kubernetes 与 AKS 的边界强于单容器 Docker 开发模式。Docker 模式中 Agent
和路由器位于同一容器，UID 与网络隔离不等同于生产。

### 2. 文件系统边界

Agent 只获得任务需要的 Workspace 与 Runtime 文件。良好的研发 Sandbox 使用
固定 Revision 的临时 Checkout 或 Worktree，不会挂载开发者 Home、SSH 目录、
全局 Git Credential Store 或无关仓库。

KARS 定义 Runtime Sandbox，但平台团队仍需谨慎设计 Volume 与 Secret。
NetworkPolicy 无法保护被错误挂载到 Agent 容器中的 Secret。

### 3. 网络边界

Agent 把受控请求发送到 `127.0.0.1:8443` 或文档规定的 Proxy 路径。Egress Guard
与 Kubernetes NetworkPolicy 阻止独立路径，路由器执行真正的策略决定。

必须区分：

- 网络控制回答：“这个 Packet 能否从其他路径离开？”
- 路由器策略回答：“这个模型、工具、主机或操作是否允许？”

纵深防御同时需要两者。

### 4. 身份边界

生产环境中，路由器根据部署模式使用 Workload Identity 或每 Sandbox Entra
Agent ID。Forge 不会得到对应 Azure 凭据。

本地 Kubernetes 会复现 Pod 与网络形态，但使用静态提供商凭据进行开发。它拥有
接近生产的基础设施形态，却不是生产身份。

### 5. 生命周期与证据边界

Controller 观察 `karsSandbox`、创建或更新资源，并报告 Conditions。路由器记录
请求期间的决定。任务结束后，可以删除 Workspace，同时把审计证据独立导出。

临时执行可以降低持久化风险，但在导出证据前删除 Pod，也可能破坏重要事故上下文。

## 检查 Sandbox，而不是假设

启动第 2 章的本地 Kubernetes 环境，然后定位 Sandbox：

```bash
kubectl get karssandboxes -n kars-system
kubectl get karssandbox dev-agent -n kars-system -o yaml
kars inspect dev-agent
```

定位生成的 Pod 并检查形态：

```bash
kubectl get pods -A
kubectl describe pod <sandbox-pod> -n <sandbox-namespace>
kubectl get pod <sandbox-pod> -n <sandbox-namespace> \
  -o jsonpath='{range .spec.initContainers[*]}init:{.name}{"\n"}{end}{range .spec.containers[*]}container:{.name} uid:{.securityContext.runAsUser}{"\n"}{end}'
```

检查网络 Safety Net：

```bash
kubectl get networkpolicy -A
kubectl describe networkpolicy <sandbox-policy> -n <sandbox-namespace>
```

然后关联一次请求：

```bash
kars connect dev-agent
kars logs dev-agent --service router -f
```

证据应连接 Sandbox 资源、多容器 Pod、不同 UID、NetworkPolicy 和路由器事件。

## 使用 Forge 测试边界

请创建一次性测试仓库，绝不要使用生产 Checkout 进行以下实验。

| 测试 | 预期结果 |
| --- | --- |
| 读取分配 Workspace 中的文件 | 允许 |
| 读取开发者 Home 中的 Secret | 文件未挂载或不可访问 |
| 通过路由器调用模型 | 在推理策略范围内允许 |
| 直接访问未知主机 | Block/Deny |
| 以 root 执行进程 | 被 Security Context 阻止 |
| 重启 Agent | Controller 将工作负载恢复到期望状态 |
| 引用不存在的推理策略 | Sandbox Condition 变为 Degraded |

每项结果都要记录产生它的控制。“命令失败”还不够；需要判断原因是文件系统布局、
UID、Egress Guard、NetworkPolicy、路由器策略还是协调。

## 选择正确隔离级别

KARS 使用安全的 Sandbox 默认值，包括 Enhanced Isolation、严格 Seccomp Profile
和 Default-Deny 网络。AKS 可以选择由 Kata/AMD SEV-SNP 支持的 Confidential
Isolation，进一步加强工作负载隔离。

当 Forge 处理未发布源码或高价值构建输入时，机密隔离可能合适。但它不能取代
最小权限身份、签名镜像、工具策略、出口策略或代码审查。

## Sandbox 不承诺什么

团队把以下限制写入威胁模型：

- 它不能证明生成的 Patch 一定正确。
- 它不会让不可信代码自动变得可以合并。
- 它无法保护被错误挂载到 Agent 中的凭据。
- 它不会把 Docker 开发模式变成生产边界。
- 它不能取代租户级 RBAC、配额、镜像策略或审计导出。
- 如果策略明确允许任意 Shell 和不受限出口，它也无法补偿。

Sandbox 负责限制权限；测试、评估、评审和部署策略仍然决定变更是否可接受。

## Forge Sandbox 设计记录

继续之前，团队记录：

```text
Workload：一次 Forge Builder 任务
Source：固定 Revision 的临时 Checkout
Agent User：UID 1000
Router User：UID 1001
外部路径：仅 Router
Agent 中的凭据：无
可写范围：仅任务 Workspace
生命周期 Owner：KARS Controller
证据目标：外部 Audit Store
清理：导出证据和 Patch 后删除 Workspace
```

下一章会把已经理解的 Runtime 边界转化为可评审的 Kubernetes 契约。

## 完成定义

只有固定 Revision 的一次性 Checkout 被挂载到 Forge、Agent 不持有可复用 Git
或模型凭据、直接访问未知目标失败、UID 隔离清晰可见，并且 Workspace 清理后审计
证据仍保留时，开发环境才算 Ready。

## 官方参考

- [架构与部署模式](https://github.com/Azure/kars/blob/main/docs/architecture.md)
- [karsSandbox CRD 参考](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md#karssandbox--the-agent)
- [Runtime 契约](https://github.com/Azure/kars/blob/main/docs/runtimes.md)
- [安全模型](https://github.com/Azure/kars/blob/main/docs/security.md)
