from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


class ControlViolation(RuntimeError):
    def __init__(self, status_code: int, code: str, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class Handoff:
    issue_id: str
    revision: str
    patch_digest: str
    test_evidence_digest: str
    producer: str = "maf-builder"
    consumer: str = "independent-reviewer"
    model: str = "gpt-5.6-sol"

    def digest(self) -> str:
        payload = json.dumps(
            asdict(self),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        return f"sha256:{hashlib.sha256(payload).hexdigest()}"


class AuditChain:
    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def append(self, event: str, decision: str, metadata: dict[str, Any]) -> None:
        with self._lock:
            previous_hash = self._entries[-1]["hash"] if self._entries else "GENESIS"
            body = {
                "timestamp": datetime.now(UTC).isoformat(),
                "event": event,
                "decision": decision,
                "metadata": metadata,
                "previousHash": previous_hash,
            }
            canonical = json.dumps(
                body,
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
            body["hash"] = hashlib.sha256(canonical).hexdigest()
            self._entries.append(body)

    def snapshot(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(entry) for entry in self._entries]

    def verify(self) -> bool:
        previous_hash = "GENESIS"
        for entry in self.snapshot():
            body = {key: value for key, value in entry.items() if key != "hash"}
            if body["previousHash"] != previous_hash:
                return False
            canonical = json.dumps(
                body,
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
            if hashlib.sha256(canonical).hexdigest() != entry["hash"]:
                return False
            previous_hash = entry["hash"]
        return True


class TaskLedger:
    def __init__(self, concurrency_limit: int, daily_limit: int) -> None:
        self._slots = threading.BoundedSemaphore(concurrency_limit)
        self._daily_limit = daily_limit
        self._usage: dict[str, int] = {}
        self._day = datetime.now(UTC).date()
        self._lock = threading.Lock()

    def acquire(self, customer: str) -> None:
        if not self._slots.acquire(blocking=False):
            raise ControlViolation(429, "concurrency_limit", "task concurrency limit reached")
        try:
            with self._lock:
                today = datetime.now(UTC).date()
                if today != self._day:
                    self._day = today
                    self._usage.clear()
                if sum(self._usage.values()) >= self._daily_limit:
                    raise ControlViolation(429, "daily_task_limit", "daily task limit reached")
                self._usage[customer] = self._usage.get(customer, 0) + 1
        except Exception:
            self._slots.release()
            raise

    def release(self) -> None:
        self._slots.release()

    def report(self) -> dict[str, Any]:
        with self._lock:
            return {
                "day": self._day.isoformat(),
                "dailyLimit": self._daily_limit,
                "totalTasks": sum(self._usage.values()),
                "customers": dict(sorted(self._usage.items())),
            }


def digest_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode()).hexdigest()}"
