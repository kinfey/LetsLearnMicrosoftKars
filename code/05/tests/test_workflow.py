from __future__ import annotations

import unittest

from host_agent.workflow import (
    ALLOWED_ISSUE,
    ALLOWED_TEST,
    WORKFLOW,
    WorkflowState,
    contract_for,
)


class WorkflowTests(unittest.TestCase):
    def test_contract_stops_for_human_review(self) -> None:
        contract = contract_for(ALLOWED_ISSUE)
        self.assertEqual(contract.allowed_test, ALLOWED_TEST)
        self.assertEqual(contract.states, WORKFLOW)
        self.assertEqual(contract.states[-1], WorkflowState.STOP_FOR_HUMAN_REVIEW)
        self.assertNotIn("MERGE", [state.value for state in contract.states])
        self.assertNotIn("DEPLOY", [state.value for state in contract.states])

    def test_unknown_issue_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside the approved scope"):
            contract_for("UNAPPROVED-1")


if __name__ == "__main__":
    unittest.main()
