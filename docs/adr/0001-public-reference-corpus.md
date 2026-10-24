# 0001. Public reference corpus: NIST AI RMF 1.0 and Generative AI Profile

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

Phase 1 needs a fixed corpus to build the evaluation dataset and the baseline RAG against.
The corpus must:

- be public, with terms that allow storing, chunking and quoting it;
- come from an authoritative source that can be cited and checksummed;
- contain no confidential client, institutional or operational data;
- have enough internal structure to make metadata-aware retrieval (Phase 2) meaningful;
- support every query class in the evaluation dataset: answerable, unanswerable, ambiguous and high-risk.

## Decision

Use two NIST publications as the reference corpus:

| `doc_id` | Publication | Date | DOI | Pages | SHA-256 |
|---|---|---|---|---|---|
| `nist-ai-100-1` | NIST AI 100-1, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)* | January 2023 | [10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1) | 48 | `7576edb531d9848825814ee88e28b1795d3a84b435b4b797d3670eafdc4a89f1` |
| `nist-ai-600-1` | NIST AI 600-1, *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile* | July 2024 | [10.6028/NIST.AI.600-1](https://doi.org/10.6028/NIST.AI.600-1) | 64 | `6e73620ab6b64e90ef2c04bf0e0d6246185a2f4b1b13cab0df494496cff89b6a` |

Both files were retrieved on 2026-10-24 from the official NIST publication server
(`https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf` and `.../NIST.AI.600-1.pdf`).

The PDFs are **not committed**. `data/corpus/manifest.toml` records source URL, identifiers,
checksum and license for each document, and `scripts/download_corpus.py` downloads the files
into the git-ignored `data/corpus/raw/` and fails if a checksum does not match.

### Why these documents

- **Domain fit.** The project is about governed AI systems; a corpus about AI risk management
  makes it natural to write high-risk and accountability-sensitive evaluation queries.
- **Structure.** AI 100-1 organizes its Core into functions (GOVERN, MAP, MEASURE, MANAGE),
  categories and subcategories. AI 600-1 maps suggested actions onto the same subcategories.
  This gives stable section paths for metadata filtering and claim-level citations.
- **Natural abstention cases.** Both documents are voluntary guidance. Questions about legal
  obligations, specific products or other jurisdictions are out of their scope, which
  produces realistic unanswerable and high-risk queries.
- **Size.** 112 pages in total is small enough to inspect by hand when labeling the evaluation set.

## License and attribution

Source: NIST, [Copyright, Fair Use, and Licensing Statements for SRD, Data, Software, and Technical Series Publications](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications)
(NIST AI 600-1 links to this page as its copyright, use and licensing statement).
For NIST Technical Series Publications, that page states that:

- works authored by NIST employees are not subject to copyright protection within the United States;
- foreign rights are reserved;
- the public is granted a non-exclusive, perpetual, paid-up, royalty-free, worldwide right to
  reprint these works;
- reprints should use the recommended citation and include the line
  *"Republished courtesy of the National Institute of Standards and Technology."*

The page also notes that some NIST-published works may be written by third parties and be
subject to copyright. Both publications in this corpus list the National Institute of Standards
and Technology as author.

**How this repository complies:**

- Any excerpt that is published from this repository (evaluation datasets, reports, examples)
  carries the citation of its source document and the line
  *"Republished courtesy of the National Institute of Standards and Technology."*
- Citations follow this form:
  - National Institute of Standards and Technology (2023) *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. (Department of Commerce, Washington, D.C.), NIST Artificial Intelligence (AI) Report, NIST AI 100-1. https://doi.org/10.6028/NIST.AI.100-1 (accessed 2026-10-24)
  - National Institute of Standards and Technology (2024) *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile*. (Department of Commerce, Washington, D.C.), NIST Artificial Intelligence (AI) Report, NIST AI 600-1. https://doi.org/10.6028/NIST.AI.600-1 (accessed 2026-10-24)
- This project is independent. Using these documents does not imply endorsement by NIST, and the
  repository does not use NIST logos.

## Alternatives considered

- **EU AI Act (Regulation (EU) 2024/1689) now.** Deferred to Phase 2. A binding regulation next to
  voluntary guidance is the best test for metadata-aware retrieval and for keeping the system from
  presenting a recommendation as a legal obligation, but it adds little before the baseline exists.
- **ISO/IEC 42001 and other standards.** Rejected. They are copyrighted and cannot be redistributed
  or quoted freely.
- **A synthetic corpus.** Rejected. It would make the evaluation easier to control but would not
  reflect the ambiguity and cross-references of real governance documents.

## Consequences

- The evaluation dataset (Phase 1) is written against these two documents and their section paths.
- Every document entry carries `jurisdiction` and `legal_status`. For this corpus they are `US`
  and `voluntary`, so the system has no basis to answer questions about legal obligations and
  must route them accordingly.
- The metadata schema (`src/governed_rag/retrieval/corpus.py`) is designed to take a second
  corpus without changes:
  - document identifiers are a free mapping (`doi` today; `celex` and `eli` for EU law);
  - `document_type`, `jurisdiction` and `legal_status` already include the values the EU AI Act needs;
  - chunk `section_path` is a list of headings that fits both the NIST hierarchy
    (`["GOVERN", "GOVERN 1", "GOVERN 1.1"]`) and the regulation's
    (`["Chapter III", "Article 9", "Paragraph 2"]`);
  - licenses are declared once per corpus and referenced by id.
- **Phase 2 follow-up:** before adding the EU AI Act, verify and record the reuse terms of
  EUR-Lex content and which language version is used, in a new ADR or an update to this one.
- If NIST publishes a revision (AI 100-1 states that a formal review is expected no later than
  2028), the new version is added as a new manifest entry with its own checksum, not by
  overwriting the existing one.
