# 1. Why KARS?

## Learning objectives

By the end of this chapter, you will be able to explain the risk of giving an
agent direct credentials and network access, describe the KARS data path, and
choose an appropriate KARS deployment mode.

## The agent infrastructure problem

An AI agent does more than generate text. It can call tools, read data, make
network requests, and act for a user. A prompt injection or faulty plan can
therefore become a real infrastructure incident.

Traditional application controls are necessary but insufficient. If the agent
process owns cloud credentials and unrestricted egress, the same process that
interprets untrusted content also controls the security boundary.

KARS—Agent Reference Stack for Kubernetes—uses a different invariant:

> The agent has no independent path to external services or Azure credentials.

Each agent runs in a Kubernetes sandbox with a dedicated inference router. The
router mediates inference, identity, tool calls, content-safety observations,
budgets, egress, and audit events. Kubernetes isolation and NetworkPolicy make
the router the intended external data path.

## Core components

| Component | Responsibility |
| --- | --- |
| KARS controller | Reconciles custom resources into pods, services, policies, and identity resources |
| Agent container | Runs the selected framework or custom agent as UID 1000 |
| Inference router | Brokers external access and enforces policy |
| Egress guard | Establishes the sandbox network path |
| A2A gateway/core | Handles agent-to-agent exposure and routing |
| KARS CLI | Wraps local, Kubernetes, Azure, Helm, and operational workflows |

The unit of work is a `KarsSandbox`. Policy resources describe what that
sandbox may infer, call, and reach.

## Three deployment shapes

### Local Docker

`kars dev --release` puts the agent and router in one container. It is the
fastest smoke test, but it does not reproduce the production container or
NetworkPolicy boundary.

### Local Kubernetes

`kars dev --release --target local-k8s` creates a kind cluster and deploys the
production-shaped multi-container pod. This is the recommended learning mode.

### AKS

`kars up` provisions the managed Kubernetes path with Azure identity options
and optional confidential isolation. Use this after validating workloads
locally.

## Project status

KARS is open-source, self-hosted alpha software. Its APIs use
`kars.azure.com/v1alpha1`; breaking changes can occur between minor releases.
It is a reference implementation rather than a managed service and has no
Microsoft product SLA. Some advanced trust, A2A verification, attestation, and
supply-chain admission capabilities remain incomplete.

This guide pins examples to `v0.1.25`. Treat the upstream source, CRD schemas,
and `kars <command> --help` as authoritative.

## Checkpoint

You are ready to continue if you can answer:

1. Why should the agent process not own external credentials?
2. Which component enforces inference and egress policy?
3. Why is local Kubernetes more representative than local Docker?

## Official references

- [README](https://github.com/Azure/kars/blob/main/README.md)
- [Architecture](https://github.com/Azure/kars/blob/main/docs/architecture.md)
- [Maturity](https://github.com/Azure/kars/blob/main/docs/maturity.md)
- [Security](https://github.com/Azure/kars/blob/main/docs/security.md)
