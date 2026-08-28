# 4. 平台：把演示变成 Kubernetes 契约

> **交付阶段：** 共享开发平台
> **新问题：** 每位工程师和 CI Job 如何复现相同的 Forge 环境？
> **交付物：** 可评审的 `karsSandbox` 与 `InferencePolicy` Manifest。

## 命令记录的问题

创业团队招聘了第一位新工程师。Forge 已在 Maya 的本地集群运行，但没人能回答
一个简单评审问题：“我们到底批准
了什么？”

终端历史包含命令、默认值、重试和实验，却无法描述稳定的期望状态。Ethan 要求
团队将 Forge 表达为可评审、可 Diff、可持续协调的 Kubernetes 资源。

## 从两项职责开始

团队把工作负载与推理权限分开：

- `karsSandbox` 描述 Forge 如何运行。
- `InferencePolicy` 描述 Forge 可以使用的推理路径。

策略是必需的，并与沙箱位于同一命名空间，避免应用 Manifest 静默回退到不受
限制的内联推理。

## 编写第一份契约

创建 `forge.yaml`：

```yaml
apiVersion: kars.azure.com/v1alpha1
kind: InferencePolicy
metadata:
  name: forge-inference
  namespace: kars-system
  labels:
    app.kubernetes.io/name: forge
spec:
  appliesTo:
    sandboxName: forge
  modelPreference:
    primary:
      provider: azure-openai
      deployment: gpt-4.1
---
apiVersion: kars.azure.com/v1alpha1
kind: karsSandbox
metadata:
  name: forge
  namespace: kars-system
  labels:
    app.kubernetes.io/name: forge
spec:
  runtime:
    kind: OpenClaw
    openclaw:
      config:
        agent:
          model: azure/gpt-4.1
  inferenceRef:
    name: forge-inference
```

提供商和 Deployment 只是示例，Maya 会根据实际账号调整。

应用前，团队检查：

- 策略是否指向正确沙箱？
- 沙箱是否引用正确策略？
- 两者是否都位于 `kars-system`？
- 当前 KARS 版本是否真正支持该 Runtime？

然后执行：

```bash
kubectl diff -f forge.yaml
kubectl apply -f forge.yaml
kubectl get karssandbox forge -n kars-system -w
```

## 把状态看作一场对话

Kubernetes `spec` 是团队提出的请求，`status` 是 Controller 的回答。

```bash
kubectl get karssandbox forge -n kars-system -o yaml
kubectl describe karssandbox forge -n kars-system
kars status forge
```

`Ready=True` 表示 Controller 报告协调成功，并不表示所有 Forge 代码修改都正确
或安全。

Lina 故意把 `inferenceRef.name` 改为 `missing-policy`，沙箱随即进入 Degraded。
团队先读取 `status.conditions`，而不是直接查看 Pod 日志。Condition 指出了无法
解析的依赖；他们恢复引用并观察协调自动恢复。

这次实验形成了一条长期有效的调试规则：

> 调试生成资源之前，先读取 Owner Resource 的 Conditions。

## 只在需要时扩展资源

设计评审中，团队把后续需求映射到 CRD：

| Forge 需求 | KARS 资源 |
| --- | --- |
| 运行研发进程 | `karsSandbox` |
| 选择模型并限制推理 | `InferencePolicy` |
| 只允许读取、Patch 与测试工具 | `ToolPolicy` |
| 注册源码与研发工具服务 | `McpServer` |
| 保存允许的 Memory | `karsMemory` |
| 运行回归用例 | `karsEval` |
| 描述可信 Peer | `TrustGraph` |
| 临时访问某个主机 | `EgressApproval` |
| 治理运维操作 | `karsSREAction` |
| 暴露 Peer Endpoint | `A2AAgent` |

他们不会为了“完整”而创建所有资源。每项资源必须对应具体需求，高级功能还必须
检查上游成熟度表。

## 观察协调过程

团队在 Git 中修改模型 Deployment：

```bash
kubectl diff -f forge.yaml
kubectl apply -f forge.yaml
kubectl get karssandbox forge -n kars-system -w
```

他们观察 Controller 更新生成配置和状态。没人直接修改生成的 ConfigMap，因为
协调会覆盖这种修改，并隐藏真正的 Source of Truth。

## 决定字段所有者

本地实验使用 `kubectl apply` 即可。生产环境计划使用 Argo CD 或 Flux。团队提前
建立一条规则：

> 一个字段只有一个 Owner。

如果 GitOps 管理推理策略，运维人员在正常操作中就不使用命令式 CLI 修改同一策略。
紧急变更必须回写 Git，或被明确回滚。

## 失败场景

依次测试：

1. 引用不存在的 `InferencePolicy`。
2. 将策略和沙箱放入不同命名空间。
3. 使用当前版本未实现的 Runtime。
4. 使用无效的提供商 Deployment。

每次记录：

- `karsSandbox` Condition；
- 是否创建 Pod；
- 路由器或 Controller 错误；
- 恢复 Ready 所需的最小 Manifest 修改。

## 本章结果

Forge 不再是“Maya 周一输入过的那些命令”，而是一份可版本化的契约。下一次评审
讨论的是 Diff，而不是某个人的记忆。

同一契约今天可以选择 OpenClaw，之后可以选择 MAF Python。Runtime 代码发生变化，
但必需的推理引用、Sandbox 控制、Router 和状态模型仍属于平台职责。

## 完成定义

当全新集群能够协调 Manifest、缺失 Policy 会产生有用的 Degraded Condition、
`kubectl diff` 能显示每项权限变化，并且 CI 而非创始人的 Shell History 能复现
环境时，平台契约才算 Ready。

## 官方参考

- [CRD 参考](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md)
- [基础 Agent 示例](https://github.com/Azure/kars/tree/main/examples/basic-agent)
- [架构](https://github.com/Azure/kars/blob/main/docs/architecture.md)
