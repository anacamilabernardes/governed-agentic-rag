# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Python 3.12, managed with uv. CI (`.github/workflows/ci.yml`) runs exactly these, in this order:

```bash
uv sync --locked                 # install; fails if uv.lock is stale (run `uv lock` after editing deps)
uv run ruff check .
uv run ruff format --check .     # `uv run ruff format .` to fix
uv run mypy                      # strict, src/ only (configured in pyproject.toml)
uv run pytest
```

Single test: `uv run pytest tests/unit/test_routing.py::test_low_confidence_requires_human_review`

Download and checksum-verify the reference corpus (not needed for tests, which use no network):
`uv run python scripts/download_corpus.py`

## Architecture

The project is built in roadmap phases (see README). Phase 0 is done: the LangGraph flow exists with
**stub nodes**, and real logic arrives in later phases. Each new component is supposed to be evaluated
against the baseline RAG (Phase 1) before the next phase.

### Graph (`src/governed_rag/orchestration/`)

- `graph.py` wires the flow from the README's mermaid diagram: classify → retrieve → filter_by_metadata →
  rerank → check_source_sufficiency → generate → validate_citations → assess_confidence_and_risk, ending
  in one of three terminal nodes: `answer`, `abstain`, `human_review`.
- Node implementations live in their domain packages (`classification/`, `retrieval/`, `generation/`,
  `governance/`). Nodes take `RAGState` and return a partial-update dict.
- `build_graph(overrides)` replaces nodes by name. Integration tests use it to reach every terminal route
  with synthetic nodes, and it is the intended hook for the baseline and evaluation.
- `routing.py` holds pure conditional-edge functions. They **fail closed**: a missing gate result routes
  to `abstain` (or `human_review` after assessment), never to `answer`.
- Terminal nodes record *why* a route was taken. `abstain` infers its reason from which gate failed,
  checked in flow order (`in_scope` → `evidence_sufficient` → `citations_valid`), so gate nodes must set
  their boolean.
- `Route` enum values (`answer` / `abstain` / `human_review`) are the expected-route labels of the
  evaluation dataset; keep them in sync.

LangGraph constraints that already shaped the code:
- A node name cannot equal a state key. This is why the output field is `final_answer`, not `answer`.
- `Node` is a `Protocol` with a parameter named `state`. A plain `Callable[[RAGState], ...]` fails
  mypy strict against LangGraph's `add_node` overloads.

### Governance semantics (from README, enforced by tests)

Abstention (insufficient evidence), human review (evidence may suffice but risk/accountability needs a
human) and human rejection (a reviewer vetoes an evidence-backed draft) are **distinct outcomes** and
must stay distinguishable in state and metrics. Risk is classified early but carried in state, so a
reviewer receives a full evidence package rather than a bare query. The human decision step
(approve / revise / reject) is not implemented yet (Phase 3).

### Corpus (`data/corpus/`, `src/governed_rag/retrieval/corpus.py`)

- The corpus is NIST AI 100-1 and AI 600-1 (decision, license and attribution in
  `docs/adr/0001-public-reference-corpus.md`). PDFs are **not committed**. `manifest.toml` pins source
  URL and SHA-256, and files are downloaded to the git-ignored `data/corpus/raw/`.
- The Pydantic schema is designed to take the EU AI Act in Phase 2 unchanged: `jurisdiction`,
  `legal_status` (voluntary vs binding, so guidance is never presented as legal obligation), free-form
  `identifiers`, list-based `section_path`, and licenses declared once and referenced by id.
- A new document version is a new manifest entry with its own checksum, not an in-place edit.
- Excerpts published from this repo (eval datasets, reports) must carry the source citation and NIST's
  reprint line (`reprint_line` in the manifest).
- Before adding the EU AI Act, verify and record EUR-Lex reuse terms (follow-up noted in ADR 0001).

## Conventions

- Language: everything committed to the repository is in English: code, comments, docs, ADRs, README,
  commit messages, PR descriptions and the evaluation dataset. Conversation with the maintainer is in
  Portuguese.
- Public or synthetic data only. Tests use synthetic placeholder strings.
- ADRs in `docs/adr/` are numbered in the order decisions are made. Update the index in
  `docs/adr/README.md`. ADR 0002 (low-confidence routing to human review) is planned.
- Only mark README roadmap items done once verified.
- Workflow used so far: one branch per task, small Conventional Commits, PR to `main` merged with a merge
  commit (not squash) to keep individual commits.
