#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

[[ "${ROLLBACK_IMAGE}" == *.azurecr.io/*@sha256:* ]] \
  || fail "Set ROLLBACK_IMAGE to the previously approved ACR digest"
kubectl --context "${KARS_KUBE_CONTEXT}" -n kars-system patch \
  "karssandbox/${KARS_SANDBOX_NAME}" --type=merge \
  -p "{\"spec\":{\"runtime\":{\"byo\":{\"image\":\"${ROLLBACK_IMAGE}\",\"contractVersion\":\"v1\"}}}}" \
  >/dev/null
pass "Rollback image was applied; verify the Sandbox phase and run make verify"
