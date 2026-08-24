# Let's Learn Microsoft KARS

A bilingual, story-driven guide to [Azure KARS](https://github.com/Azure/kars),
the Agent Reference Stack for Kubernetes. Follow a startup AI team from product
requirements through development, testing, and production deployment.

English is the canonical edition. The Chinese edition is maintained as a
chapter-for-chapter translation.

> This guide tracks KARS `v0.1.25` (reviewed on 2026-08-24). KARS is an alpha
> reference implementation, not an officially supported Microsoft product.
> Confirm commands against `kars --help` when using another version.

## Read the tutorial

- [English (default)](docs/en/README.md)
- [简体中文](docs/zh-cn/README.md)

## Learning path

| Chapter | Delivery stage | New problem solved | Runtime focus |
| --- | --- | --- | --- |
| 1 | Requirements | Bound an issue-to-PR product before writing code | Architecture |
| 2 | Prototype | Prove the user journey locally in one day | OpenClaw |
| 3 | Development environment | Protect customer source and credentials | Shared sandbox |
| 4 | Platform contract | Make every environment reproducible and reviewable | Both |
| 5 | Cost and authority | Control tokens, tools, dependencies, and egress | Both |
| 6 | Framework decision | Move from conversational prototype to coded workflow | OpenClaw → MAF Python |
| 7 | Testing | Test behavior, policy, security, and regressions | MAF + `KarsEval` |
| 8 | Deployment | Promote safely through CI/CD to AKS | MAF production, OpenClaw canary |
| 9 | Release | Deliver one requirement from issue to reviewed patch | End to end |

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
