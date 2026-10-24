"""Conditional-edge routers. Each one reads state and returns the name of the next node."""

from typing import Literal

from governed_rag.orchestration.state import RAGState

# Placeholder until thresholds move to configs/ and are calibrated against the baseline.
CONFIDENCE_THRESHOLD = 0.7


def route_after_classification(state: RAGState) -> Literal["retrieve", "abstain"]:
    return "retrieve" if state.get("in_scope", False) else "abstain"


def route_after_sufficiency_gate(state: RAGState) -> Literal["generate", "abstain"]:
    return "generate" if state.get("evidence_sufficient", False) else "abstain"


def route_after_citation_validation(
    state: RAGState,
) -> Literal["assess_confidence_and_risk", "abstain"]:
    return "assess_confidence_and_risk" if state.get("citations_valid", False) else "abstain"


def route_after_assessment(state: RAGState) -> Literal["answer", "human_review"]:
    if state.get("requires_human_accountability", False):
        return "human_review"
    if state.get("confidence", 0.0) < CONFIDENCE_THRESHOLD:
        return "human_review"
    return "answer"
