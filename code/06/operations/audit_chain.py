from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class AuditRecord:
    payload: dict[str, object]
    previous_hash: str
    record_hash: str


def digest(previous_hash: str, payload: dict[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{previous_hash}\n{canonical}".encode()).hexdigest()


def build_chain(payloads: Iterable[dict[str, object]]) -> list[AuditRecord]:
    records: list[AuditRecord] = []
    previous_hash = "0" * 64
    for payload in payloads:
        record_hash = digest(previous_hash, payload)
        records.append(AuditRecord(payload, previous_hash, record_hash))
        previous_hash = record_hash
    return records


def verify_chain(records: Iterable[AuditRecord]) -> bool:
    previous_hash = "0" * 64
    for record in records:
        if record.previous_hash != previous_hash:
            return False
        if record.record_hash != digest(previous_hash, record.payload):
            return False
        previous_hash = record.record_hash
    return True
