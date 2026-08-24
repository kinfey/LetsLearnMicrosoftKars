# 6. 安全、可观测性与运维

## 分层控制

KARS 组合了多种控制：

- 容器隔离和可选的机密隔离；
- Kubernetes NetworkPolicy 与路由器代理出口；
- 使用工作负载身份，而不是在 Agent 中存放凭据；
- 推理和工具策略；
- 内容安全观测；
- Token 预算和速率限制；
- 防篡改审计链。

没有任何单一层能够保证任意 Agent 行为安全。设计时要同时考虑预防、检测与恢复。

## 运维命令

```bash
kars status hello
kars inspect hello
kars logs hello --service router -f
kars audit tail hello --decision deny -f
kars trace hello --network
```

查看集群整体状态：

```bash
kars operator
kars headlamp --install
```

使用 `kars eval run <evaluation-name>`，让策略和模型变更接受可重复评估，而不是
仅依赖人工提示测试。

## 事件响应流程

沙箱出现异常时：

1. 保留沙箱状态、Kubernetes 事件和路由器审计输出。
2. 停止暴露或撤销批准，但不要删除证据。
3. 确认相关提示、工具调用、身份、目标和策略决定。
4. 轮换任何可能泄露的外部 Secret。
5. 修正策略或工作负载代码。
6. 恢复前重新运行评估和出口拒绝测试。

审计日志具备防篡改能力，但当前链头签名和完整不可否认性仍在路线图中。请将日志
导出到独立控制的系统。

## 生产加固清单

- 将 KARS、策略包和工作负载镜像固定到不可变版本/Digest。
- 将出口从学习模式切换到强制执行。
- 使用具名工具授权，不使用通配符。
- 设置单请求和每日预算。
- 使用工作负载身份，绝不注入长期提供商 Secret。
- 应用命名空间配额、Pod 安全控制和租户边界。
- 导出指标、Trace 和审计日志。
- 测试恢复、升级和事件响应流程。
- 依赖高级功能前先检查成熟度矩阵。

不同提供商的安全遥测并不相同。Foundry 可以返回详细的提示过滤结果；Copilot 和
GitHub Models 在服务端过滤，但不会提供同等的路由器可见类别/严重级别数据。

## 练习

触发一个允许请求和一个被拒绝的目标。在路由器日志中找到两者，解释策略决定，
并记录建立事件时间线所需的证据。

## 官方参考

- [安全](https://github.com/Azure/kars/blob/main/docs/security.md)
- [成熟度](https://github.com/Azure/kars/blob/main/docs/maturity.md)
- [CLI 参考](https://github.com/Azure/kars/blob/main/docs/cli-reference.md)
