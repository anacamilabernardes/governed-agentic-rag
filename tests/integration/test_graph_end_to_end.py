from typing import Any

import pytest

from governed_rag.orchestration.graph import build_graph
from governed_rag.orchestration.state import (
    AbstentionReason,
    EscalationReason,
    Evidence,
    RAGState,
    Route,
)

EVIDENCE: list[Evidence] = [
    {"source_id": "doc-1", "text": "Supporting text.", "score": 0.9, "metadata": {}}
]


def _retrieve_one(state: RAGState) -> dict[str, Any]:
    return {"candidates": EVIDENCE}


def _generate_cited(state: RAGState) -> dict[str, Any]:
    return {"draft": "Answer.", "citations": [{"claim": "Answer.", "source_ids": ["doc-1"]}]}


def _generate_uncited(state: RAGState) -> dict[str, Any]:
    return {"draft": "Answer.", "citations": [{"claim": "Answer.", "source_ids": ["doc-9"]}]}


def _confident(state: RAGState) -> dict[str, Any]:
    return {"confidence": 0.95}


def test_default_stubs_abstain_for_lack_of_evidence() -> None:
    result = build_graph().invoke({"query": "q"})
    assert result["route"] == Route.ABSTAIN
    assert result["abstention_reason"] == AbstentionReason.INSUFFICIENT_EVIDENCE


def test_out_of_scope_query_abstains() -> None:
    graph = build_graph({"classify": lambda s: {"in_scope": False}})
    result = graph.invoke({"query": "q"})
    assert result["route"] == Route.ABSTAIN
    assert result["abstention_reason"] == AbstentionReason.OUT_OF_SCOPE
    assert "candidates" not in result


def test_unsupported_citation_abstains() -> None:
    graph = build_graph({"retrieve": _retrieve_one, "generate": _generate_uncited})
    result = graph.invoke({"query": "q"})
    assert result["route"] == Route.ABSTAIN
    assert result["abstention_reason"] == AbstentionReason.UNSUPPORTED_CLAIMS


def test_low_confidence_escalates_to_human_review() -> None:
    graph = build_graph({"retrieve": _retrieve_one, "generate": _generate_cited})
    result = graph.invoke({"query": "q"})
    assert result["route"] == Route.HUMAN_REVIEW
    assert result["escalation_reason"] == EscalationReason.LOW_CONFIDENCE


def test_accountability_escalates_with_evidence_package() -> None:
    graph = build_graph(
        {
            "classify": lambda s: {"in_scope": True, "requires_human_accountability": True},
            "retrieve": _retrieve_one,
            "generate": _generate_cited,
            "assess_confidence_and_risk": _confident,
        }
    )
    result = graph.invoke({"query": "q"})
    assert result["route"] == Route.HUMAN_REVIEW
    assert result["escalation_reason"] == EscalationReason.ACCOUNTABILITY_REQUIRED
    assert result["evidence"] == EVIDENCE
    assert result["draft"] == "Answer."


def test_grounded_confident_answer_is_released() -> None:
    graph = build_graph(
        {
            "retrieve": _retrieve_one,
            "generate": _generate_cited,
            "assess_confidence_and_risk": _confident,
        }
    )
    result = graph.invoke({"query": "q"})
    assert result["route"] == Route.ANSWER
    assert result["final_answer"] == "Answer."


def test_unknown_override_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown node"):
        build_graph({"nonexistent": lambda s: {}})
