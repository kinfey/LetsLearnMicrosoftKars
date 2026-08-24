# 3. Kubernetes API 与核心概念

## 使用协调，而不是脚本

KARS 通过自定义资源扩展 Kubernetes。你声明期望的 Agent 和策略，Controller
持续协调所需的命名空间对象、Pod、Service、策略投影和状态。

两个基础资源是：

- `KarsSandbox`：运行时、镜像/配置、隔离和策略引用。
- `InferencePolicy`：提供商、模型偏好、预算和推理控制。

推理策略是必需的，并且必须与沙箱位于同一命名空间。

## 最小 Manifest

将以下内容保存为 `hello.yaml`，并根据你的账号调整提供商和 Deployment：

```yaml
apiVersion: kars.azure.com/v1alpha1
kind: InferencePolicy
metadata:
  name: hello-inference
  namespace: kars-system
spec:
  appliesTo:
    sandboxName: hello
  modelPreference:
    primary:
      provider: azure-openai
      deployment: gpt-4.1
---
apiVersion: kars.azure.com/v1alpha1
kind: KarsSandbox
metadata:
  name: hello
  namespace: kars-system
spec:
  runtime:
    kind: OpenClaw
    openclaw:
      config:
        agent:
          model: azure/gpt-4.1
  inferenceRef:
    name: hello-inference
```

应用并观察：

```bash
kubectl apply -f hello.yaml
kubectl get karssandbox hello -n kars-system -w
kubectl describe karssandbox hello -n kars-system
kars status hello
```

调试生成的 Pod 之前，请先读取 `status.conditions`。Degraded 条件通常会更直接
地说明无效运行时或无法解析的策略引用。

## 资源地图

| 资源 | 用途 |
| --- | --- |
| `KarsSandbox` | Agent 工作负载和运行时 |
| `InferencePolicy` | 模型、预算和推理控制 |
| `ToolPolicy` | 工具允许规则和速率限制 |
| `McpServer` | MCP Endpoint 和身份验证元数据 |
| `KarsMemory` | Memory 配置 |
| `KarsEval` | 评估工作负载 |
| `TrustGraph` | Mesh 信任关系 |
| `EgressApproval` | 有时限的网络批准 |
| `KarsSREAction` | 受治理的运维操作 |
| `A2AAgent` | Agent 间暴露 |

`KarsAuthConfig` 和 `KarsPairing` 由基础设施管理。不同 CRD 的成熟度并不相同，
请检查上游成熟度表。

## 声明式工作流

应用更改前使用 `kubectl diff -f hello.yaml`。在共享环境中，把 Manifest 存入
Git，并由 Argo CD 或 Flux 协调。避免 CLI 命令和 GitOps 同时管理相同字段。

## 练习

1. 部署 Manifest。
2. 将 Deployment 名称改为无效值。
3. 观察沙箱和路由器状态。
4. 恢复有效值并确认协调完成。
5. 使用 `kubectl delete -f hello.yaml` 删除资源。

## 官方参考

- [CRD 参考](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md)
- [基础 Agent 示例](https://github.com/Azure/kars/tree/main/examples/basic-agent)
- [架构](https://github.com/Azure/kars/blob/main/docs/architecture.md)
