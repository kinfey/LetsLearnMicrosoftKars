# Let's Learn Microsoft KARS

This nine-chapter course follows **ByteCraft AI**, a four-person startup racing
to launch Forge, an issue-to-pull-request development Agent, without gambling
its runway or its first customer's source code. Every chapter starts with a new
delivery problem and ends with an engineering decision or testable artifact.

The team deliberately uses two frameworks:

- **OpenClaw** for the first conversational prototype and fast tool iteration.
- **Microsoft Agent Framework (MAF) Python** when the workflow must become
  explicit, testable application code.

KARS keeps the sandbox, router, policy, audit, and network controls consistent
while the application framework changes.

## Contents

1. [Requirement: Bound the Product Before the Demo](01-why-kars.md)
2. [Prototype: Build the First OpenClaw Vertical Slice](02-local-quickstart.md)
3. [Development: Protect the Customer Repository](03-inside-the-sandbox.md)
4. [Platform: Turn the Demo into a Kubernetes Contract](04-kubernetes-api.md)
5. [Governance: Control Tokens, Tools, and Egress](05-policies-and-tools.md)
6. [Framework: Move from OpenClaw to MAF Python](06-runtimes-and-byo.md)
7. [Testing: Stop Forge from Fixing the Same Test Forever](07-security-and-operations.md)
8. [Deployment: Promote Forge to AKS](08-aks-and-multi-agent.md)
9. [Release: Deliver an Issue-to-PR Workflow](09-applied-project.md)

## The startup team

| Person | Startup role | Main concern |
| --- | --- | --- |
| Maya | Co-founder and AI engineer | Ship useful Agent behavior |
| Arun | Product lead | Solve the customer's development bottleneck |
| Ethan | Platform engineer | Make environments reproducible and operable |
| Lina | Security engineer | Bound source, identity, tools, cost, and egress |

## Conventions

- Commands use a POSIX-compatible shell.
- Replace values in `<angle-brackets>`.
- Examples use the `kars-system` namespace.
- Local Kubernetes is the default learning environment.
- Production guidance assumes AKS.

[简体中文版本](../zh-cn/README.md)
