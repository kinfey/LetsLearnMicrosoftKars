# Let's Learn Microsoft KARS

A bilingual, hands-on guide to [Azure KARS](https://github.com/Azure/kars), the
Agent Reference Stack for Kubernetes.

English is the canonical edition. The Chinese edition is maintained as a
chapter-for-chapter translation.

> This guide tracks KARS `v0.1.25` (reviewed on 2026-08-24). KARS is an alpha
> reference implementation, not an officially supported Microsoft product.
> Confirm commands against `kars --help` when using another version.

## Read the tutorial

- [English (default)](docs/en/README.md)
- [简体中文](docs/zh-cn/README.md)

## Learning path

| Chapter | Topic | Outcome |
| --- | --- | --- |
| 1 | Mental model | Understand why agents need a mediated runtime |
| 2 | Local quickstart | Run and connect to an agent locally |
| 3 | Inside the sandbox | Understand process, filesystem, network, identity, and lifecycle boundaries |
| 4 | Kubernetes API | Define sandboxes and inference policies |
| 5 | Policies and tools | Govern inference, tools, MCP, and egress |
| 6 | Runtimes and BYO | Select an adapter or integrate an image |
| 7 | Security and operations | Inspect, audit, trace, and harden a sandbox |
| 8 | AKS and multi-agent | Operate identity, mesh, A2A, and GitOps |
| 9 | Applied project | Build a governed software development Agent |

## Language synchronization

Every English chapter at `docs/en/NN-*.md` has a matching Chinese chapter at
`docs/zh-cn/NN-*.md`. Keep headings, code blocks, links, warnings, and chapter
order equivalent. Commands and API names remain in English.

## Official sources

The tutorial summarizes the upstream project; the upstream documentation is
authoritative:

- [KARS repository](https://github.com/Azure/kars)
- [Getting started](https://github.com/Azure/kars/blob/main/docs/getting-started.md)
- [Architecture](https://github.com/Azure/kars/blob/main/docs/architecture.md)
- [CRD reference](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md)
- [CLI reference](https://github.com/Azure/kars/blob/main/docs/cli-reference.md)
- [Security](https://github.com/Azure/kars/blob/main/docs/security.md)
- [Maturity](https://github.com/Azure/kars/blob/main/docs/maturity.md)

## License

Unless stated otherwise, this tutorial is released under the [MIT License](LICENSE).
