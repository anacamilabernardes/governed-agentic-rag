"""Typed state shared by every node in the governed RAG graph."""

from enum import StrEnum
from typing import NotRequired, TypedDict


class Route(StrEnum):
    """Terminal route of a query. Matches the expected-route labels used in evaluation."""

    ANSWER = "answer"
    ABSTAIN = "abstain"
    HUMAN_REVIEW = "human_review"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AbstentionReason(StrEnum):
    OUT_OF_SCOPE = "out_of_scope"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    UNSUPPORTED_CLAIMS = "unsupported_claims"


class EscalationReason(StrEnum):
    ACCOUNTABILITY_REQUIRED = "accountability_required"
    LOW_CONFIDENCE = "low_confidence"


class HumanDecision(StrEnum):
    APPROVE = "approve"
    REVISE = "revise"
    REJECT = "reject"


class Evidence(TypedDict):
    source_id: str
    text: str
    score: float
    metadata: dict[str, str]


class Citation(TypedDict):
    claim: str
    source_ids: list[str]


class RAGState(TypedDict):
    query: str

    # Classification
    in_scope: NotRequired[bool]
    risk_level: NotRequired[RiskLevel]
    requires_human_accountability: NotRequired[bool]

    # Retrieval
    candidates: NotRequired[list[Evidence]]
    evidence: NotRequired[list[Evidence]]
    evidence_sufficient: NotRequired[bool]

    # Generation
    draft: NotRequired[str]
    citations: NotRequired[list[Citation]]
    citations_valid: NotRequired[bool]
    confidence: NotRequired[float]

    # Outcome
    route: NotRequired[Route]
    abstention_reason: NotRequired[AbstentionReason]
    escalation_reason: NotRequired[EscalationReason]
    human_decision: NotRequired[HumanDecision]
    final_answer: NotRequired[str]
