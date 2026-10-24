from governed_rag.orchestration.routing import (
    CONFIDENCE_THRESHOLD,
    route_after_assessment,
    route_after_citation_validation,
    route_after_classification,
    route_after_sufficiency_gate,
)
from governed_rag.orchestration.state import RAGState


def test_out_of_scope_query_abstains() -> None:
    assert route_after_classification({"query": "q", "in_scope": False}) == "abstain"


def test_in_scope_query_proceeds_to_retrieval() -> None:
    assert route_after_classification({"query": "q", "in_scope": True}) == "retrieve"


def test_insufficient_evidence_abstains() -> None:
    assert route_after_sufficiency_gate({"query": "q", "evidence_sufficient": False}) == "abstain"


def test_sufficient_evidence_proceeds_to_generation() -> None:
    assert route_after_sufficiency_gate({"query": "q", "evidence_sufficient": True}) == "generate"


def test_invalid_citations_abstain() -> None:
    assert route_after_citation_validation({"query": "q", "citations_valid": False}) == "abstain"


def test_missing_gate_results_fail_closed() -> None:
    state: RAGState = {"query": "q"}
    assert route_after_classification(state) == "abstain"
    assert route_after_sufficiency_gate(state) == "abstain"
    assert route_after_citation_validation(state) == "abstain"
    assert route_after_assessment(state) == "human_review"


def test_accountability_requires_human_review_even_with_high_confidence() -> None:
    state: RAGState = {"query": "q", "requires_human_accountability": True, "confidence": 1.0}
    assert route_after_assessment(state) == "human_review"


def test_low_confidence_requires_human_review() -> None:
    state: RAGState = {"query": "q", "confidence": CONFIDENCE_THRESHOLD - 0.01}
    assert route_after_assessment(state) == "human_review"


def test_confident_low_risk_answer_is_released() -> None:
    state: RAGState = {"query": "q", "confidence": CONFIDENCE_THRESHOLD}
    assert route_after_assessment(state) == "answer"
