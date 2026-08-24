# 2. 本地快速入门

## 前置条件

在 macOS 或 Linux 上准备：

- Node.js 22 或更高版本
- Docker、Podman 或 nerdctl
- `kind`
- `kubectl`
- GitHub Copilot 席位、Azure AI Foundry 部署或 GitHub Models Token

检查工具：

```bash
node --version
docker version
kind version
kubectl version --client
```

## 安装 CLI

```bash
npm install --global @kars-runtime/cli
kars --version
```

为了让实验可复现，请显式指定版本：

```bash
kars dev --release v0.1.25 --target local-k8s
```

该命令会创建 kind 集群、安装 KARS 并启动开发 Agent。按照提示完成所选推理
服务提供商的身份验证。

## 检查环境

```bash
kubectl get pods -n kars-system
kars list
kars status dev-agent
kars inspect dev-agent
```

确认沙箱已经就绪，且 Agent 与路由器位于不同容器。如果 Pod 未就绪，检查
Kubernetes 事件和路由器日志：

```bash
kubectl describe pod -n kars-system <pod-name>
kars logs dev-agent --service router
```

## 连接 Agent

```bash
kars connect dev-agent
```

尝试一个无害提示：

```text
请解释哪个组件控制你的网络访问。
```

响应由所选模型生成，但请求会经过沙箱路由器。

## 停止实验

```bash
kars dev down
```

只在需要更快冒烟测试时使用 Docker 模式：

```bash
kars dev --release v0.1.25
```

Docker 模式成功不代表生产隔离或 NetworkPolicy 已得到验证。

## 故障排查

| 现象 | 首要检查项 |
| --- | --- |
| 找不到 `kars` | 全局 npm 二进制目录是否在 `PATH` 中 |
| 集群创建失败 | 容器引擎是否正在运行 |
| 沙箱持续 Pending | `kubectl describe pod` 中的事件 |
| 推理返回 401/403 | 登录、Endpoint、Deployment 或 Token |
| 命令参数不同 | `kars <command> --help` 与已安装版本 |

## 练习

启动本地 Kubernetes 环境，保存 `kars inspect dev-agent` 的输出，连接一次，
然后关闭环境。清理前找出 Agent 容器、路由器容器和 NetworkPolicy。

## 官方参考

- [快速入门](https://github.com/Azure/kars/blob/main/docs/quickstart.md)
- [开始使用](https://github.com/Azure/kars/blob/main/docs/getting-started.md)
- [CLI 参考](https://github.com/Azure/kars/blob/main/docs/cli-reference.md)
