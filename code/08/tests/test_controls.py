import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "pilot_agent"))

from controls import AuditChain, ControlViolation, Handoff, TaskLedger, digest_text


def test_handoff_is_digest_pinned() -> None:
    handoff = Handoff(
        issue_id="FAB-482",
        revision=digest_text("revision"),
        patch_digest=digest_text("patch"),
        test_evidence_digest=digest_text("tests"),
    )
    assert handoff.digest().startswith("sha256:")
    assert len(handoff.digest()) == 71


def test_audit_chain_detects_valid_history() -> None:
    chain = AuditChain()
    chain.append("intake", "approved", {"issueId": "FAB-482"})
    chain.append("tool", "denied", {"tool": "shell"})
    assert chain.verify()
    assert len(chain.snapshot()) == 2


def test_daily_customer_usage_is_reported() -> None:
    ledger = TaskLedger(concurrency_limit=1, daily_limit=2)
    ledger.acquire("fabrikam")
    ledger.release()
    ledger.acquire("contoso")
    ledger.release()
    assert ledger.report()["customers"] == {"contoso": 1, "fabrikam": 1}
    with pytest.raises(ControlViolation, match="daily task limit"):
        ledger.acquire("fabrikam")


def test_concurrency_limit_fails_closed() -> None:
    ledger = TaskLedger(concurrency_limit=1, daily_limit=10)
    ledger.acquire("fabrikam")
    with pytest.raises(ControlViolation, match="concurrency"):
        ledger.acquire("contoso")
    ledger.release()
