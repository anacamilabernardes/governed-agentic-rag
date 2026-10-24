"""Intent and risk classification. Stub until Phase 2."""

from typing import Any

from governed_rag.orchestration.state import RAGState, RiskLevel


def classify(state: RAGState) -> dict[str, Any]:
    return {
        "in_scope": True,
        "risk_level": RiskLevel.LOW,
        "requires_human_accountability": False,
    }
