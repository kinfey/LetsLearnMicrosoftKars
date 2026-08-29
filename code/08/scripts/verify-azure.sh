#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

namespace="kars-${KARS_SANDBOX_NAME}"
port="${PILOT_PORT:-18088}"
router_port="${ROUTER_PORT:-18446}"
pf_pid=""
router_pf_pid=""
cleanup() {
  for pid in "${pf_pid}" "${router_pf_pid}"; do
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      kill "${pid}"
      wait "${pid}" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT

pod="$(kubectl --context "${KARS_KUBE_CONTEXT}" -n "${namespace}" get pod \
  -l "kars.azure.com/sandbox=${KARS_SANDBOX_NAME}" \
  -o jsonpath='{.items[0].metadata.name}')"
node="$(kubectl --context "${KARS_KUBE_CONTEXT}" -n "${namespace}" get pod \
  "${pod}" -o jsonpath='{.spec.nodeName}')"
arch="$(kubectl --context "${KARS_KUBE_CONTEXT}" get node "${node}" \
  -o jsonpath='{.metadata.labels.kubernetes\.io/arch}')"
[[ "${arch}" == "amd64" ]] || fail "Pilot is not running on amd64"

kubectl --context "${KARS_KUBE_CONTEXT}" -n "${namespace}" port-forward \
  "deployment/${KARS_SANDBOX_NAME}" "${port}:8080" \
  >"${EVIDENCE_DIR}/port-forward.log" 2>&1 &
pf_pid=$!
kubectl --context "${KARS_KUBE_CONTEXT}" -n "${namespace}" port-forward \
  "deployment/${KARS_SANDBOX_NAME}" "${router_port}:8443" \
  >"${EVIDENCE_DIR}/router-port-forward.log" 2>&1 &
router_pf_pid=$!
for _ in $(seq 1 60); do
  curl -fsS "http://127.0.0.1:${port}/healthz" >/dev/null 2>&1 && break
  sleep 2
done

curl -fsS -H 'content-type: application/json' \
  --data '{"issue_id":"FAB-482","customer":"fabrikam","requirement":"Missing optional customer note must not return 500"}' \
  "http://127.0.0.1:${port}/intake" |
  jq . >"${EVIDENCE_DIR}/intake.json"

curl -fsS -H 'content-type: application/json' \
  --data '{"issue_id":"FAB-482","customer":"fabrikam","scenario":"normal"}' \
  "http://127.0.0.1:${port}/run" |
  jq . >"${EVIDENCE_DIR}/success.json"
jq -e '
  .model == "gpt-5.6-sol"
  and (.reply | contains("KARS_APPLIED_PROJECT_GPT_5_6_SOL_OK"))
  and .nextAction == "STOP_FOR_HUMAN_PR_APPROVAL"
  and (.handoff.digest | startswith("sha256:"))
' "${EVIDENCE_DIR}/success.json" >/dev/null

for scenario in unknown_tool unknown_host builder_self_approve; do
  status="$(curl -sS -o "${EVIDENCE_DIR}/denied-${scenario}.json" \
    -w '%{http_code}' -H 'content-type: application/json' \
    --data "{\"issue_id\":\"FAB-482\",\"customer\":\"fabrikam\",\"scenario\":\"${scenario}\"}" \
    "http://127.0.0.1:${port}/run")"
  [[ "${status}" == "403" ]] || fail "${scenario} was not denied"
done

curl -fsS "http://127.0.0.1:${port}/contract" |
  jq . >"${EVIDENCE_DIR}/contract.json"
jq -e '
  .model == "gpt-5.6-sol"
  and .runtimeKind == "BYO"
  and .contractVersion == "v1"
  and (.providerCredentialNames | length == 0)
' "${EVIDENCE_DIR}/contract.json" >/dev/null

curl -fsS "http://127.0.0.1:${port}/usage" |
  jq . >"${EVIDENCE_DIR}/usage.json"
curl -fsS "http://127.0.0.1:${port}/audit" |
  jq . >"${EVIDENCE_DIR}/application-audit.json"
jq -e '.integrity == "valid" and .entries >= 5' \
  "${EVIDENCE_DIR}/application-audit.json" >/dev/null
curl -fsS "http://127.0.0.1:${router_port}/agt/audit/verify" |
  jq . >"${EVIDENCE_DIR}/router-audit.json"
jq -e '.integrity == "valid" and .entries >= 1' \
  "${EVIDENCE_DIR}/router-audit.json" >/dev/null

kubectl --context "${KARS_KUBE_CONTEXT}" -n kars-system get \
  "karssandbox/${KARS_SANDBOX_NAME}" -o json |
  jq '{name:.metadata.name,phase:.status.phase,image:.spec.runtime.byo.image,suspended:.spec.suspended}' \
  >"${EVIDENCE_DIR}/sandbox.json"
kubectl --context "${KARS_KUBE_CONTEXT}" -n kars-system get \
  inferencepolicy/fabrikam-release-inference -o json |
  jq '{generation:.metadata.generation,observedGeneration:.status.observedGeneration,compiledDigest:.status.compiledDigest,loadedDigest:.status.loadedDigest}' \
  >"${EVIDENCE_DIR}/policy.json"
jq -e '
  .generation == .observedGeneration
  and (.loadedDigest | startswith("sha256:"))
  and .loadedDigest == .compiledDigest
' "${EVIDENCE_DIR}/policy.json" >/dev/null

cleanup
trap - EXIT
pass "Azure success path, three denials, amd64, policy, usage, audit, and credential boundary passed"
