#!/usr/bin/env bash
set -euo pipefail

requested_deploy="${DEPLOY_AZURE:-}"
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
[[ -z "${requested_deploy}" ]] || DEPLOY_AZURE="${requested_deploy}"
[[ "${DEPLOY_AZURE}" == "true" ]] \
  || fail "Azure deployment is opt-in. Set DEPLOY_AZURE=true."

exec > >(tee "${EVIDENCE_DIR}/azure-deploy.log") 2>&1

state="$(az aks show \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --name "${AKS_NAME}" \
  --query provisioningState -o tsv 2>/dev/null || true)"
[[ "${state}" == "Succeeded" ]] \
  || fail "Existing AKS ${AZURE_RESOURCE_GROUP}/${AKS_NAME} must be Succeeded"

location="$(az aks show \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --name "${AKS_NAME}" \
  --query location -o tsv)"
if [[ -n "${AZURE_LOCATION}" && "${AZURE_LOCATION}" != "${location}" ]]; then
  fail "Configured AZURE_LOCATION does not match existing AKS location ${location}"
fi

az aks get-credentials \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --name "${AKS_NAME}" \
  --overwrite-existing \
  --only-show-errors >/dev/null
kubectl --context "${KARS_KUBE_CONTEXT}" get deployment \
  -n kars-system kars-controller >/dev/null
pass "Existing AKS and KARS control plane are ready"

image_tag="applied-$(git -C "${REPO_ROOT}" rev-parse --short=12 HEAD)"
az acr build \
  --registry "${KARS_ACR_NAME}" \
  --image "fabrikam-release-pilot:${image_tag}" \
  --platform linux/amd64 \
  --file "${LAB_ROOT}/pilot_agent/Dockerfile" \
  "${LAB_ROOT}/pilot_agent" \
  --only-show-errors >/dev/null
image_digest="$(az acr repository show-tags \
  --name "${KARS_ACR_NAME}" \
  --repository fabrikam-release-pilot \
  --detail \
  --query "[?name=='${image_tag}'].digest | [0]" \
  -o tsv)"
[[ "${image_digest}" == sha256:* ]] || fail "Could not resolve ACR image digest"
FORGE_IMAGE="${KARS_ACR_NAME}.azurecr.io/fabrikam-release-pilot@${image_digest}"
export FORGE_IMAGE
printf '%s\n' "${FORGE_IMAGE}" >"${STATE_DIR}/current-image"
pass "Linux amd64 Pilot image is pinned by digest"

"${LAB_ROOT}/scripts/setup.sh"
"${LAB_ROOT}/scripts/render.sh"
"${LAB_ROOT}/scripts/validate.sh"

kubectl --context "${KARS_KUBE_CONTEXT}" apply \
  -f "${RENDERED_DIR}/release-pilot.yaml" >/dev/null

phase=""
for _ in $(seq 1 120); do
  phase="$(kubectl --context "${KARS_KUBE_CONTEXT}" -n kars-system get \
    "karssandbox/${KARS_SANDBOX_NAME}" \
    -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  [[ "${phase}" == "Running" ]] && break
  sleep 5
done
[[ "${phase}" == "Running" ]] || fail "${KARS_SANDBOX_NAME} did not reach Running"

namespace="kars-${KARS_SANDBOX_NAME}"
kubectl --context "${KARS_KUBE_CONTEXT}" -n "${namespace}" apply -f - >/dev/null <<YAML
apiVersion: v1
kind: Service
metadata:
  name: fabrikam-dev-tools
spec:
  selector:
    kars.azure.com/sandbox: ${KARS_SANDBOX_NAME}
  ports:
    - name: mcp
      port: 8080
      targetPort: 8080
YAML
kubectl --context "${KARS_KUBE_CONTEXT}" apply \
  -f "${RENDERED_DIR}/mcp-and-eval.yaml" >/dev/null
pass "Release Pilot, MCP metadata, and evaluation declaration are deployed"

"${LAB_ROOT}/scripts/verify-azure.sh"
