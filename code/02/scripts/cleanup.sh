#!/usr/bin/env bash
set -euo pipefail

kubectl label namespace kars-forge kars.azure.com/break-glass- >/dev/null 2>&1 || true
kubectl -n kars-system delete karssandbox forge-missing-policy \
  --ignore-not-found --wait=true >/dev/null

echo "Removed code/02 temporary cluster state. Local evidence was preserved."
