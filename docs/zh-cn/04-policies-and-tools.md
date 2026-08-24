# 4. 推理、工具、MCP 与出口策略

## 策略层

KARS 将工作负载代码与治理分离：

1. `InferencePolicy` 选择模型并设置 Token 预算。
2. `ToolPolicy` 控制工具使用和速率限制。
3. `McpServer` 注册工具服务器及其身份验证要求。
4. 出口策略控制沙箱可以访问的目标。

平台团队可以据此管理 Guardrail，应用团队则负责 Agent 提示和逻辑。

## 推理预算

通过 CLI 创建或更新策略：

```bash
kars ip apply daily-budget \
  --sandbox hello \
  --model gpt-4.1 \
  --token-budget 100000
```

预算可限制影响范围和成本，但不能取代 Azure 配额或成本警报。应检查实际资源，
而不是仅凭 CLI 成功退出就假设路由器已经加载策略：

```bash
kars policy show hello
kubectl get inferencepolicy -n kars-system -o yaml
```

## 工具策略

以下命令创建带明确速率限制的宽松开发规则：

```bash
kars tp apply dev-tools \
  --tool '*' \
  --rps 10 \
  --burst 20
```

生产环境应将 `*` 替换为具名工具，并只授予 Agent 所需的操作。

## 注册 MCP

使用 OAuth 元数据和允许的工具注册生产 MCP Server：

```bash
kars mcp apply research-mcp \
  --url https://mcp.example.com \
  --production-mode \
  --oauth-issuer https://login.example.com \
  --oauth-audience mcp-api \
  --allowed-tool search
```

不要把 MCP 凭据写入 Agent 镜像。应通过平台契约管理身份和访问。

## 学习、批准、强制执行

KARS 出口默认为学习模式。学习模式会记录未知且不在阻止列表中的主机，但它不是
严格的生产强制策略。

```bash
kars egress hello --learn
# 只执行预期工作流。
kars egress hello --learned
kars egress hello --approve api.github.com
kars egress hello --enforce
```

请人工审查每个学习到的目标，不要自动批准整个列表：学习期间，不可信内容可能
故意触发非预期主机。临时例外应使用带 TTL 的 `EgressApproval`，不要永久扩大
基线。

## 签名策略包

高级环境可将策略打包为 OCI Artifact，按 Digest 引用并通过 cosign 验证签名。
固定 Digest 可防止 Tag 漂移，签名验证可确认发布者意图。只有当路由器报告已
加载预期 Digest 后，沙箱才应进入 Ready 状态。

## 练习

为沙箱设置每日推理预算，只允许一个具名工具，在学习模式观察必要网络目标，批准
最小集合并切换为强制执行。确认未批准目标在审计流中被拒绝。

## 官方参考

- [CLI 参考](https://github.com/Azure/kars/blob/main/docs/cli-reference.md)
- [CRD 参考](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md)
- [安全](https://github.com/Azure/kars/blob/main/docs/security.md)
