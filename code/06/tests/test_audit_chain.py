from __future__ import annotations

import unittest
from dataclasses import replace

from operations.audit_chain import build_chain, verify_chain


class AuditChainTests(unittest.TestCase):
    def test_detects_modified_record(self) -> None:
        records = build_chain(
            [
                {"action": "inference", "decision": "allow"},
                {"action": "egress", "decision": "deny"},
            ]
        )
        self.assertTrue(verify_chain(records))

        records[0] = replace(
            records[0],
            payload={"action": "inference", "decision": "deny"},
        )
        self.assertFalse(verify_chain(records))


if __name__ == "__main__":
    unittest.main()
