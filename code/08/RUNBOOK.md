# Fabrikam Release Pilot Runbook

Everything starts with OpenClaw Intake. Do not run Builder work until `/intake`
returns the pinned requirement and revision.

## Status and evidence

```bash
kars status fabrikam-release-pilot
kars inspect fabrikam-release-pilot
kars logs fabrikam-release-pilot --service router
kars audit tail fabrikam-release-pilot
kars trace fabrikam-release-pilot --network
kubectl -n kars-system get karssandbox fabrikam-release-pilot
```

Run the executable acceptance suite with `make verify`. Preserve `.evidence/`
before suspension, rollback, or redeployment.

## Kill switch

`make suspend` sets `spec.suspended=true` after exporting the Sandbox resource.
It stops new work without deleting the CR or the exported evidence. Use
`make resume` to restore service.

## Rollback

Set `ROLLBACK_IMAGE` in the ignored `config/azure.env` to a previously approved
ACR `@sha256:` reference, run `make rollback`, and then run `make verify`.

## Ownership

- Support owner: configured by `SUPPORT_OWNER`.
- Application changes: Pull Request review.
- KARS policy changes: platform/security review.
- Production deployment: CI/GitOps, never the Builder Agent.
