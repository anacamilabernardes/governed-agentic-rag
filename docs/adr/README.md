# Architecture Decision Records

Consequential design and technology decisions, numbered in the order they are made.
A superseded ADR is kept and marked as such, never deleted.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-public-reference-corpus.md) | Public reference corpus: NIST AI RMF 1.0 and Generative AI Profile | Accepted |
| 0002 | Route low-confidence outputs to human review after evidence sufficiency | Planned |

## Template

New ADRs are named `NNNN-short-title.md` and use this structure:

```markdown
# NNNN. Title

- **Status:** Proposed | Accepted | Superseded by NNNN
- **Date:** YYYY-MM-DD

## Context

What forces the decision, and what constraints apply.

## Decision

What was decided.

## Alternatives considered

Each option, and why it was not chosen.

## Consequences

What becomes easier, what becomes harder, and what follow-up work is needed.
```
