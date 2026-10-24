"""Terminal nodes. Each records the route taken and why."""

from typing import Any

from governed_rag.orchestration.state import (
    AbstentionReason,
    EscalationReason,
    RAGState,
    Route,
)


def answer(state: RAGState) -> dict[str, Any]:
    return {"route": Route.ANSWER, "final_answer": state.get("draft", "")}


def abstain(state: RAGState) -> dict[str, Any]:
    if not state.get("in_scope", False):
        reason = AbstentionReason.OUT_OF_SCOPE
    elif not state.get("evidence_sufficient", False):
        reason = AbstentionReason.INSUFFICIENT_EVIDENCE
    else:
        reason = AbstentionReason.UNSUPPORTED_CLAIMS
    return {"route": Route.ABSTAIN, "abstention_reason": reason}


def human_review(state: RAGState) -> dict[str, Any]:
    # The reviewer's decision (approve / revise / reject) is added in Phase 3.
    if state.get("requires_human_accountability", False):
        reason = EscalationReason.ACCOUNTABILITY_REQUIRED
    else:
        reason = EscalationReason.LOW_CONFIDENCE
    return {"route": Route.HUMAN_REVIEW, "escalation_reason": reason}
