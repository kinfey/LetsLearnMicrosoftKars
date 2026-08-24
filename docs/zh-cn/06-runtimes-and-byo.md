# 6. 把 Forge 迁入受治理的 Runtime

## 一个令人不安的发现

策略原型使用 OpenClaw，但 Maya 最初的 Forge 是带自定义仓库索引和 Patch
规划的 Python 应用。完全重写会延误项目；原样运行旧容器又会保留直接凭据和
网络假设。

团队选择第三条路：保留应用逻辑，替换权限模型。

## 有意识地选择 Adapter

KARS 包含 OpenClaw、Hermes、OpenAI Agents、Microsoft Agent Framework
Python、LangGraph Python/TypeScript、Anthropic、Pydantic-AI 和自带镜像
（BYO）Adapter。

团队按需求比较：

| 应用情况 | 合理起点 |
| --- | --- |
| 探索完整 Mesh/Handoff | OpenClaw 或 Hermes |
| 已有 OpenAI Agents 代码 | OpenAI Agents Adapter |
| 已有图工作流 | LangGraph Adapter |
| 自定义进程与依赖 | BYO |

Schema 中存在枚举值并不代表 Runtime 已完整支持。他们会在当前版本的 Runtime
矩阵和成熟度文档中确认。

## 盘点旧容器

修改代码前，Maya 记录现有假设：

```text
AZURE_OPENAI_API_KEY -> 由 Forge 读取
AZURE_OPENAI_ENDPOINT -> 直接调用
GITHUB_TOKEN -> 传给仓库和 Pull Request 工具
HTTPS_PROXY -> 不受限制的公司代理
process user -> root
```

每一项都与目标沙箱契约冲突。

## 重构权限边界

BYO 镜像必须：

- 以 UID 1000 运行；
- 通过 `127.0.0.1:8443` 的路由器发送受控外部请求；
- 不包含 Azure 或模型提供商凭据；
- 遵循已记录的沙箱环境契约；
- 只写入允许运行时路径。

Maya 将模型和工具 Endpoint 从硬编码提供商 URL 改为配置，删除 Agent 获取凭据
的逻辑，并把工具身份验证移入 KARS/MCP 平台配置。

应用仍然决定检查哪些代码、运行哪些测试，平台则决定该操作是否得到授权。

## 分层测试

团队不会直接从 `docker run` 跳到 AKS。

### 1. 进程测试

以 UID 1000 运行容器，验证启动、健康状态和可写路径。

### 2. 无凭据测试

检查运行环境和镜像历史。即使提示 Forge 枚举环境，它也不应找到提供商 Key。

### 3. 路由器路径测试

发送一次模型请求，并将其与路由器审计事件对应。如果路由器不可用时请求仍成功，
说明 Forge 还有未预期的外部路径。

### 4. 负向网络测试

尝试访问无关公网主机。直接访问必须失败。团队不会通过恢复通用代理来“修复”它。

### 5. 策略测试

测试允许的代码读取与测试、未知工具、速率耗尽、Token 预算耗尽和 MCP 故障。

## 供应链决策

团队扫描镜像，并在推广时按 Digest 固定。KARS 官方镜像带有签名和供应链元数据，
但自动拒绝未签名 BYO 镜像尚不是完整 KARS 能力。集群需要单独执行组织的镜像
准入策略。

他们记录：

- 源码 Revision；
- 构建工作流身份；
- 镜像 Digest；
- 漏洞扫描结果；
- 基础镜像；
- KARS 版本和 Runtime Adapter；
- 策略包 Digest。

## 一个证明设计价值的 Bug

测试期间，Forge 看到仓库中的 Bootstrap 命令，并尝试从未经批准的 Package Host
下载未签名构建工具。强制出口使下载失败。

Maya 最初称它为回归，Lina 则称它为刚刚发现的能力。

团队决定构建必须使用批准 Build Image 中固定的工具链，于是删除 Forge 的
Bootstrap 行为。安全控制迫使团队做出供应链决定；此前这个行为一直隐藏在仓库
指令中。

## 迁移清单

1. 找出所有凭据和外部 Endpoint。
2. 将框架匹配到支持的 Adapter 或 BYO。
3. 让 Endpoint 可配置。
4. 删除应用持有的外部凭据。
5. 以 UID 1000 运行。
6. 通过 `127.0.0.1:8443` 路由受控调用。
7. 测试明确失败和拒绝路径。
8. 扫描并固定镜像。
9. 记录 Runtime 与策略版本。

## 本章结果

Forge 仍然包含 Contoso 的索引与 Patch 规划逻辑，但不再自行定义权限。迁移改变的是基础
设施假设，而不是业务目的。

## 官方参考

- [Runtime Adapter](https://github.com/Azure/kars/blob/main/docs/runtimes.md)
- [示例](https://github.com/Azure/kars/tree/main/examples)
- [BYO Quickstart](https://github.com/Azure/kars/tree/main/examples/byo-quickstart)
