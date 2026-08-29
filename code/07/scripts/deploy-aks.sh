#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

[[ "${DEPLOY_AKS}" == "true" ]] \
  || fail "Azure deployment is opt-in. Set DEPLOY_AKS=true after reviewing the plan."
[[ "${FORGE_IMAGE}" == *@sha256:* ]] \
  || fail "FORGE_IMAGE must be an ACR image pinned by sha256 digest"

location="$(resolve_location)"
kars up \
  --name "${KARS_SANDBOX_NAME}" \
  --model "${GITHUB_COPILOT_MODEL}" \
  --policy developer \
  --region "${location}" \
  --cluster-name "${AKS_NAME}" \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --isolation "${KARS_ISOLATION}" \
  --release "${KARS_RELEASE}" \
  --mesh-trust "${KARS_MESH_TRUST}" \
  --yes

az aks get-credentials \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --name "${AKS_NAME}" \
  --overwrite-existing >/dev/null

"${LAB_ROOT}/scripts/render-gitops.sh"
kubectl apply -f "${RENDERED_DIR}/multi-agent.yaml"

pass "AKS and the reviewed Builder/Reviewer resources were deployed"
