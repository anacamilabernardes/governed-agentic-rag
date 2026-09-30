# Governed Agentic RAG

> A work-in-progress reference architecture for evidence-grounded, evaluated and governable agentic RAG systems.

## Project Status

**Status:** Active development

This repository documents the design and incremental implementation of a governed Agentic RAG system.

The project is intentionally being built in public stages. Architecture, evaluation criteria and governance controls are defined before the full implementation so that design decisions, trade-offs and system evolution remain traceable.

### Current Roadmap

- [ ] Define public reference corpus
- [ ] Define evaluation dataset
- [ ] Implement baseline RAG
- [ ] Add intent and risk classification
- [ ] Add out-of-scope routing
- [ ] Add metadata-aware retrieval
- [ ] Add reranking
- [ ] Implement source-sufficiency gate
- [ ] Add grounded generation
- [ ] Add citation validation
- [ ] Implement explicit abstention path
- [ ] Implement human-review escalation path
- [ ] Add LangGraph orchestration
- [ ] Add structured tracing
- [ ] Build evaluation suite
- [ ] Add FastAPI service layer
- [ ] Add automated tests
- [ ] Add Docker environment
- [ ] Add CI/CD
- [ ] Add operational observability
- [ ] Publish evaluation results
- [ ] Publish final architecture case study

---

## Problem

Standard RAG systems can produce fluent answers even when retrieval quality is weak, evidence is insufficient or the query requires human accountability.

This project explores how to design a RAG system in which:

- retrieval quality is explicitly evaluated;
- insufficient evidence leads to abstention;
- high-risk decisions can require human review;
- generated claims remain traceable to sources;
- system behavior is observable;
- evaluation and governance are part of the architecture rather than post-deployment additions.

---

## Planned Architecture

```mermaid
flowchart TD
    A[User Query] --> B[Intent & Risk Classification]

    B -->|Out of Scope| C[Abstain]
    B -->|Human Accountability Required| D[Human Review]
    B -->|In Scope| E[Retrieval]

    E --> F[Metadata Filtering]
    F --> G[Reranking]
    G --> H[Source Sufficiency Gate]

    H -->|Insufficient Evidence| C
    H -->|Sufficient Evidence| I[Grounded Generation]

    I --> J[Citation Validation]
    J --> K[Confidence & Risk Assessment]

    K -->|Evidence Valid / Risk Acceptable| L[Answer]
    K -->|Evidence Insufficient| C
    K -->|Human Judgment Required| D

    D --> M[Human Decision]
    M -->|Approve / Revise| N[Reviewed Answer]
    M -->|Reject| C
