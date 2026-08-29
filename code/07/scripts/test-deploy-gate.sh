#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

if DEPLOY_AKS=false "${LAB_ROOT}/scripts/deploy-aks.sh" \
  >"${EVIDENCE_DIR}/deploy-opt-in-denial.txt" 2>&1; then
  fail "AKS deployment unexpectedly ran without explicit opt-in"
fi
grep -q "DEPLOY_AKS=true" "${EVIDENCE_DIR}/deploy-opt-in-denial.txt" \
  || fail "Deployment opt-in denial was not explicit"

if DEPLOY_AKS=true FORGE_IMAGE=forge-byo-copilot-claw:dev \
  "${LAB_ROOT}/scripts/deploy-aks.sh" \
  >"${EVIDENCE_DIR}/deploy-image-denial.txt" 2>&1; then
  fail "AKS deployment unexpectedly accepted an unpinned image"
fi
grep -q "pinned by sha256 digest" "${EVIDENCE_DIR}/deploy-image-denial.txt" \
  || fail "Unpinned image denial was not explicit"

pass "Real AKS deployment requires explicit opt-in and a digest-pinned ACR image"
