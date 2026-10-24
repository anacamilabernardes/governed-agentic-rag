"""Assembles the governed RAG graph described in the README."""

from collections.abc import Mapping
from typing import Any, Protocol

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from governed_rag.classification.classifier import classify
from governed_rag.generation.generator import generate
from governed_rag.governance.gates import (
    assess_confidence_and_risk,
    check_source_sufficiency,
    validate_citations,
)
from governed_rag.orchestration.routing import (
    route_after_assessment,
    route_after_citation_validation,
    route_after_classification,
    route_after_sufficiency_gate,
)
from governed_rag.orchestration.state import RAGState
from governed_rag.orchestration.terminals import abstain, answer, human_review
from governed_rag.retrieval.retriever import filter_by_metadata, rerank, retrieve


class Node(Protocol):
    def __call__(self, state: RAGState) -> dict[str, Any]: ...


DEFAULT_NODES: dict[str, Node] = {
    "classify": classify,
    "retrieve": retrieve,
    "filter_by_metadata": filter_by_metadata,
    "rerank": rerank,
    "check_source_sufficiency": check_source_sufficiency,
    "generate": generate,
    "validate_citations": validate_citations,
    "assess_confidence_and_risk": assess_confidence_and_risk,
    "answer": answer,
    "abstain": abstain,
    "human_review": human_review,
}


def build_graph(
    overrides: Mapping[str, Node] | None = None,
) -> CompiledStateGraph[RAGState, None, RAGState, RAGState]:
    """Compile the graph. `overrides` replaces node implementations by name."""
    overrides = overrides or {}
    unknown = set(overrides) - set(DEFAULT_NODES)
    if unknown:
        raise ValueError(f"Unknown node(s): {sorted(unknown)}")
    nodes = {**DEFAULT_NODES, **overrides}

    graph = StateGraph(RAGState)
    for name, node in nodes.items():
        graph.add_node(name, node)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", route_after_classification, ["retrieve", "abstain"])
    graph.add_edge("retrieve", "filter_by_metadata")
    graph.add_edge("filter_by_metadata", "rerank")
    graph.add_edge("rerank", "check_source_sufficiency")
    graph.add_conditional_edges(
        "check_source_sufficiency", route_after_sufficiency_gate, ["generate", "abstain"]
    )
    graph.add_edge("generate", "validate_citations")
    graph.add_conditional_edges(
        "validate_citations",
        route_after_citation_validation,
        ["assess_confidence_and_risk", "abstain"],
    )
    graph.add_conditional_edges(
        "assess_confidence_and_risk", route_after_assessment, ["answer", "human_review"]
    )
    for terminal in ("answer", "abstain", "human_review"):
        graph.add_edge(terminal, END)

    return graph.compile()
