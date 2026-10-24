"""Grounded generation with claim-level citations. Stub until Phase 3."""

from typing import Any

from governed_rag.orchestration.state import RAGState


def generate(state: RAGState) -> dict[str, Any]:
    return {"draft": "", "citations": []}
