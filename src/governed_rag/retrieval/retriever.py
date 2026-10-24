"""Retrieval, metadata filtering and reranking. Stubs until Phases 1-2."""

from typing import Any

from governed_rag.orchestration.state import RAGState


def retrieve(state: RAGState) -> dict[str, Any]:
    return {"candidates": []}


def filter_by_metadata(state: RAGState) -> dict[str, Any]:
    return {"evidence": state.get("candidates", [])}


def rerank(state: RAGState) -> dict[str, Any]:
    return {"evidence": state.get("evidence", [])}
