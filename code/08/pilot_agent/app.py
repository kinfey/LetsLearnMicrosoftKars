from __future__ import annotations

import json
import os
from typing import Any, Literal

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from controls import AuditChain, ControlViolation, Handoff, TaskLedger, digest_text
from workflow import APPROVED_TOOLS, FORBIDDEN_ACTIONS, WORKFLOW

MODEL = os.environ.get("KARS_MODEL", "")
ROUTER_URL = os.environ.get("KARS_ROUTER_URL", "http://127.0.0.1:8443")
CONTRACT_VERSION = os.environ.get("KARS_RUNTIME_CONTRACT_VERSION", "")
RUNTIME_KIND = os.environ.get("KARS_RUNTIME_KIND", "")
SUPPORT_OWNER = os.environ.get("SUPPORT_OWNER", "unassigned")
CONCURRENCY_LIMIT = int(os.environ.get("TASK_CONCURRENCY_LIMIT", "2"))
DAILY_TASK_LIMIT = int(os.environ.get("DAILY_TASK_LIMIT", "20"))
EXPECTED_MODEL = "gpt-5.6-sol"
EXPECTED_CONTRACT = "v1"
EXPECTED_KIND = "BYO"
ISSUE_ID = "FAB-482"
REVISION = "sha256:98ea5005d70f6471b35a1ab99c37d8fe34141b859b6d55e290ce1b9cbf877b43"

app = FastAPI(title="fabrikam-release-pilot")
audit = AuditChain()
ledger = TaskLedger(CONCURRENCY_LIMIT, DAILY_TASK_LIMIT)


class IntakeRequest(BaseModel):
    issue_id: str
    customer: str
    requirement: str


class RunRequest(BaseModel):
    issue_id: str
    customer: str
    scenario: Literal[
        "normal",
        "unknown_tool",
        "unknown_host",
        "repeated_loop",
        "mcp_unavailable",
        "builder_self_approve",
        "reviewer_modify_source",
        "untrusted_peer",
    ] = "normal"


def extract_output_text(events: list[dict[str, Any]]) -> str:
    deltas = [
        str(event.get("delta", ""))
        for event in events
        if event.get("type") == "response.output_text.delta"
    ]
    return "".join(deltas)


def call_router(prompt: str) -> tuple[str, list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    with httpx.stream(
        "POST",
        f"{ROUTER_URL}/v1/responses",
        headers={"authorization": "******"},
        json={
            "model": MODEL,
            "input": prompt,
            "max_output_tokens": 64,
            "stream": True,
        },
        timeout=120,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line.startswith("data: "):
                continue
            data = line[6:]
            if data != "[DONE]":
                events.append(json.loads(data))
    return extract_output_text(events), events


def reject(request: RunRequest, status: int, code: str, detail: str) -> None:
    audit.append(
        "workflow_control",
        "denied",
        {"issueId": request.issue_id, "customer": request.customer, "code": code},
    )
    raise HTTPException(status_code=status, detail={"code": code, "message": detail})


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/contract")
def contract() -> dict[str, Any]:
    return {
        "model": MODEL,
        "runtimeKind": RUNTIME_KIND,
        "contractVersion": CONTRACT_VERSION,
        "supportOwner": SUPPORT_OWNER,
        "workflow": WORKFLOW,
        "approvedTools": APPROVED_TOOLS,
        "forbiddenActions": FORBIDDEN_ACTIONS,
        "taskConcurrencyLimit": CONCURRENCY_LIMIT,
        "dailyTaskLimit": DAILY_TASK_LIMIT,
        "providerCredentialNames": [
            name
            for name in os.environ
            if ("COPILOT" in name or "GITHUB" in name)
            and ("TOKEN" in name or "KEY" in name)
        ],
    }


@app.post("/intake")
def intake(request: IntakeRequest) -> dict[str, Any]:
    if request.issue_id != ISSUE_ID:
        raise HTTPException(status_code=403, detail="issue is outside the approved pilot")
    if "customer note" not in request.requirement.lower():
        raise HTTPException(status_code=422, detail="acceptance criterion is incomplete")
    audit.append(
        "openclaw_intake",
        "approved",
        {"issueId": ISSUE_ID, "customer": request.customer, "revision": REVISION},
    )
    return {
        "stage": "OPENCLAW_INTAKE",
        "issueId": ISSUE_ID,
        "customer": request.customer,
        "revision": REVISION,
        "acceptanceCriteria": [
            "missing optional customer note does not return 500",
            "existing note behavior remains unchanged",
            "targeted tests pass",
            "human approval is required before merge or deployment",
        ],
    }


@app.post("/run")
def run(request: RunRequest) -> dict[str, Any]:
    if request.issue_id != ISSUE_ID:
        reject(request, 403, "scope_denied", "issue is outside the approved pilot")
    if (MODEL, CONTRACT_VERSION, RUNTIME_KIND) != (
        EXPECTED_MODEL,
        EXPECTED_CONTRACT,
        EXPECTED_KIND,
    ):
        reject(request, 503, "runtime_contract", "KARS runtime contract mismatch")

    denials = {
        "unknown_tool": (403, "tool_denied", "shell is not an approved tool"),
        "unknown_host": (403, "egress_denied", "unknown package host is not approved"),
        "repeated_loop": (429, "repair_limit", "repeated test loop exceeded its bound"),
        "mcp_unavailable": (503, "mcp_unavailable", "development MCP is unavailable"),
        "builder_self_approve": (
            403,
            "separation_of_duties",
            "Builder cannot approve its own patch",
        ),
        "reviewer_modify_source": (
            403,
            "separation_of_duties",
            "Reviewer cannot modify source",
        ),
        "untrusted_peer": (403, "peer_trust", "untrusted or expired peer draft rejected"),
    }
    if request.scenario in denials:
        status, code, detail = denials[request.scenario]
        reject(request, status, code, detail)

    try:
        ledger.acquire(request.customer)
    except ControlViolation as exc:
        reject(request, exc.status_code, exc.code, exc.detail)

    try:
        marker = "KARS_APPLIED_PROJECT_GPT_5_6_SOL_OK"
        reply, events = call_router(
            "You are the MAF Builder in a KARS governed release pilot. "
            "The OpenClaw Intake has approved FAB-482 at a pinned revision. "
            f"Reply on one line with exactly: {marker} FAB-482 READY_FOR_HUMAN_REVIEW"
        )
        if marker not in reply:
            raise HTTPException(status_code=502, detail="unexpected model response")

        patch = (
            '- note = payload["customer_note"].strip()\n'
            '+ note = (payload.get("customer_note") or "").strip()\n'
        )
        tests = "2 passed: missing note returns 200; supplied note remains unchanged"
        handoff = Handoff(
            issue_id=ISSUE_ID,
            revision=REVISION,
            patch_digest=digest_text(patch),
            test_evidence_digest=digest_text(tests),
        )
        audit.append(
            "builder_handoff",
            "allowed",
            {
                "issueId": ISSUE_ID,
                "customer": request.customer,
                "handoffDigest": handoff.digest(),
            },
        )
        return {
            "model": MODEL,
            "issueId": ISSUE_ID,
            "customer": request.customer,
            "workflow": WORKFLOW,
            "patch": patch,
            "tests": tests,
            "handoff": {
                **handoff.__dict__,
                "digest": handoff.digest(),
            },
            "reply": reply.strip(),
            "responseEvents": len(events),
            "nextAction": "STOP_FOR_HUMAN_PR_APPROVAL",
        }
    finally:
        ledger.release()


@app.get("/usage")
def usage() -> dict[str, Any]:
    return ledger.report()


@app.get("/audit")
def audit_log() -> dict[str, Any]:
    entries = audit.snapshot()
    return {
        "integrity": "valid" if audit.verify() else "invalid",
        "entries": len(entries),
        "events": entries,
    }


@app.post("/mcp")
def mcp_metadata() -> dict[str, Any]:
    return {
        "name": "fabrikam-dev-tools",
        "status": "available",
        "tools": APPROVED_TOOLS,
    }
