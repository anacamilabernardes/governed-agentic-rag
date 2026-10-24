"""Corpus metadata schema and manifest loader.

The schema covers the NIST corpus used from Phase 1 (ADR 0001) and is shaped to accept
binding regulation such as the EU AI Act in Phase 2 without changes.
"""

import tomllib
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]
NonEmpty = Annotated[str, Field(min_length=1)]


class DocumentType(StrEnum):
    FRAMEWORK = "framework"
    PROFILE = "profile"
    REGULATION = "regulation"
    GUIDANCE = "guidance"


class Jurisdiction(StrEnum):
    US = "US"
    EU = "EU"


class LegalStatus(StrEnum):
    """Whether a document creates obligations. Kept explicit so that voluntary guidance
    is never presented as a legal requirement."""

    VOLUNTARY = "voluntary"
    BINDING = "binding"


class StructuralUnit(StrEnum):
    # Shared
    SECTION = "section"
    APPENDIX = "appendix"
    # NIST AI RMF and profiles
    FUNCTION = "function"
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"
    ACTION = "action"
    # EU regulation
    RECITAL = "recital"
    CHAPTER = "chapter"
    ARTICLE = "article"
    PARAGRAPH = "paragraph"
    ANNEX = "annex"


class _Model(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class License(_Model):
    name: NonEmpty
    terms_url: HttpUrl
    notice: NonEmpty
    reprint_line: str | None = None


class SourceDocument(_Model):
    doc_id: Slug
    corpus_id: Slug
    title: NonEmpty
    short_title: NonEmpty
    publisher: NonEmpty
    document_type: DocumentType
    jurisdiction: Jurisdiction
    legal_status: LegalStatus
    identifiers: Annotated[dict[str, NonEmpty], Field(min_length=1)]
    version: str | None = None
    published: Annotated[str, Field(pattern=r"^\d{4}-\d{2}(-\d{2})?$")]
    language: Annotated[str, Field(pattern=r"^[a-z]{2}$")]
    source_url: HttpUrl
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    retrieved_on: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]
    license: Slug
    citation: NonEmpty


class CorpusManifest(_Model):
    schema_version: Annotated[int, Field(ge=1)]
    licenses: dict[Slug, License]
    documents: Annotated[list[SourceDocument], Field(min_length=1)]

    @model_validator(mode="after")
    def _check_references(self) -> Self:
        seen: set[str] = set()
        for doc in self.documents:
            if doc.doc_id in seen:
                raise ValueError(f"Duplicate doc_id: {doc.doc_id}")
            seen.add(doc.doc_id)
            if doc.license not in self.licenses:
                raise ValueError(f"Unknown license '{doc.license}' in {doc.doc_id}")
        return self

    def license_for(self, doc: SourceDocument) -> License:
        return self.licenses[doc.license]


class ChunkMetadata(_Model):
    """Metadata attached to every retrievable chunk. Produced by ingestion in Phase 1."""

    doc_id: Slug
    chunk_id: NonEmpty
    section_path: Annotated[list[NonEmpty], Field(min_length=1)]
    structural_unit: StructuralUnit
    page_start: Annotated[int, Field(ge=1)]
    page_end: Annotated[int, Field(ge=1)]

    @model_validator(mode="after")
    def _check_pages(self) -> Self:
        if self.page_end < self.page_start:
            raise ValueError("page_end must not be before page_start")
        return self


def load_manifest(path: Path) -> CorpusManifest:
    with path.open("rb") as f:
        return CorpusManifest.model_validate(tomllib.load(f))
