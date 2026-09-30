# Governed Agentic RAG

> Production-oriented agentic RAG architecture for reliable, evidence-grounded and governable AI systems.

## Overview

Governed Agentic RAG is a reference implementation for building LLM-based knowledge systems in environments where answers need to be traceable, evaluated and operationally controlled.

The project goes beyond basic retrieval-augmented generation by incorporating:

- agentic orchestration;
- structured retrieval;
- metadata filtering;
- reranking;
- source-sufficiency assessment;
- evidence-grounded generation;
- citation validation;
- confidence and abstention controls;
- human-in-the-loop review;
- tracing and observability;
- systematic LLM evaluation.

The objective is to demonstrate how an AI system can move from a proof of concept toward a production-oriented architecture with explicit reliability and governance controls.

---

## Architecture

```mermaid
flowchart TD
    A[User Query] --> B[Task Classification]

    B --> C[Retrieval]
    C --> D[Metadata Filtering]
    D --> E[Reranking]
    E --> F[Source Sufficiency Check]

    F -->|Sufficient| G[Grounded Generation]
    F -->|Insufficient| H[Abstain / Request Review]

    G --> I[Citation Validation]
    I --> J[Confidence & Risk Assessment]

    J -->|High Confidence| K[Answer]
    J -->|Low Confidence| H
    J -->|High Risk| L[Human Review]

    L --> M[Approved / Revised Answer]
