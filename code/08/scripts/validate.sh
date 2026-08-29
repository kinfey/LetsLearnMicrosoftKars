#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

grep -qx 'registry=https://packagefeedproxy.microsoft.io/npm/' \
  "${LAB_ROOT}/config/.npmrc" || fail "Microsoft npm source is not configured"
grep -q 'https://packagefeedproxy.microsoft.io/pypi/simple/' \
  "${LAB_ROOT}/config/pip.conf" || fail "Microsoft PyPI source is not configured"
grep -q 'https://packagefeedproxy.microsoft.io/nuget/v3/index.json' \
  "${LAB_ROOT}/config/NuGet.Config" || fail "Microsoft NuGet source is not configured"
grep -q 'ARG PIP_INDEX_URL=https://packagefeedproxy.microsoft.io/pypi/simple/' \
  "${LAB_ROOT}/pilot_agent/Dockerfile" || fail "Container PyPI source is not Microsoft proxy"

"${LAB_ROOT}/.venv/bin/python" -m pytest "${LAB_ROOT}/tests" -q

python3 - "${RENDERED_DIR}/release-pilot.yaml" <<'PY'
import sys
import yaml

documents = [doc for doc in yaml.safe_load_all(open(sys.argv[1])) if doc]
kinds = [doc["kind"] for doc in documents]
assert kinds == ["InferencePolicy", "ToolPolicy", "KarsSandbox"]
sandbox = documents[2]
assert ".azurecr.io/" in sandbox["spec"]["runtime"]["byo"]["image"]
assert "@sha256:" in sandbox["spec"]["runtime"]["byo"]["image"]
assert sandbox["spec"]["sandbox"]["runAsNonRoot"] is True
assert sandbox["spec"]["networkPolicy"]["egressMode"] == "Strict"
assert sandbox["spec"]["suspended"] is False
assert documents[0]["spec"]["modelPreference"]["primary"]["deployment"] == "gpt-5.6-sol"
PY

kubectl --context "${KARS_KUBE_CONTEXT}" apply \
  --server-side --dry-run=server \
  -f "${RENDERED_DIR}/release-pilot.yaml" >/dev/null
kubectl --context "${KARS_KUBE_CONTEXT}" apply \
  --server-side --dry-run=server \
  -f "${RENDERED_DIR}/mcp-and-eval.yaml" >/dev/null
pass "Package sources, controls, manifests, and live KARS CRDs validated"
