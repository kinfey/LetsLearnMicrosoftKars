from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WorkflowState(StrEnum):
    RECEIVE_REQUIREMENT = "RECEIVE_REQUIREMENT"
    VALIDATE_SCOPE = "VALIDATE_SCOPE"
    INSPECT_REPOSITORY = "INSPECT_REPOSITORY"
    PROPOSE_PLAN = "PROPOSE_PLAN"
    APPLY_MINIMAL_PATCH = "APPLY_MINIMAL_PATCH"
    RUN_TARGETED_TESTS = "RUN_TARGETED_TESTS"
    SUMMARIZE_EVIDENCE = "SUMMARIZE_EVIDENCE"
    STOP_FOR_HUMAN_REVIEW = "STOP_FOR_HUMAN_REVIEW"


WORKFLOW = tuple(WorkflowState)
ALLOWED_ISSUE = "FORMAT-482"
ALLOWED_TEST = "format-user"


@dataclass(frozen=True)
class ForgeContract:
    issue_id: str
    allowed_test: str
    states: tuple[WorkflowState, ...]
    forbidden_actions: tuple[str, ...] = ("MERGE", "DEPLOY")

    def to_dict(self) -> dict[str, object]:
        return {
            "issueId": self.issue_id,
            "allowedTest": self.allowed_test,
            "states": [state.value for state in self.states],
            "forbiddenActions": list(self.forbidden_actions),
        }


def contract_for(issue_id: str) -> ForgeContract:
    if issue_id != ALLOWED_ISSUE:
        raise ValueError(f"issue {issue_id!r} is outside the approved scope")
    return ForgeContract(
        issue_id=ALLOWED_ISSUE,
        allowed_test=ALLOWED_TEST,
        states=WORKFLOW,
    )
