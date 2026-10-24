from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from governed_rag.retrieval.corpus import (
    ChunkMetadata,
    CorpusManifest,
    DocumentType,
    Jurisdiction,
    LegalStatus,
    StructuralUnit,
    load_manifest,
)

MANIFEST = Path(__file__).resolve().parents[2] / "data" / "corpus" / "manifest.toml"

LICENSE: dict[str, Any] = {
    "name": "Synthetic license",
    "terms_url": "https://example.org/terms",
    "notice": "Synthetic notice for tests.",
}


def _document(**overrides: Any) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "doc_id": "doc-a",
        "corpus_id": "corpus-a",
        "title": "Synthetic document",
        "short_title": "Synthetic",
        "publisher": "Example publisher",
        "document_type": "guidance",
        "jurisdiction": "US",
        "legal_status": "voluntary",
        "identifiers": {"doi": "10.0000/example"},
        "published": "2024-01",
        "language": "en",
        "source_url": "https://example.org/doc-a.pdf",
        "sha256": "0" * 64,
        "retrieved_on": "2026-01-01",
        "license": "synthetic",
        "citation": "Example publisher (2024) Synthetic document.",
    }
    doc.update(overrides)
    return doc


def _manifest(*documents: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version": 1, "licenses": {"synthetic": LICENSE}, "documents": list(documents)}


def test_reference_manifest_is_valid() -> None:
    manifest = load_manifest(MANIFEST)

    assert [d.doc_id for d in manifest.documents] == ["nist-ai-100-1", "nist-ai-600-1"]
    for doc in manifest.documents:
        assert doc.jurisdiction is Jurisdiction.US
        assert doc.legal_status is LegalStatus.VOLUNTARY
        assert doc.source_url.host == "nvlpubs.nist.gov"
        assert manifest.license_for(doc).reprint_line


def test_duplicate_doc_id_is_rejected() -> None:
    with pytest.raises(ValidationError, match="Duplicate doc_id"):
        CorpusManifest.model_validate(_manifest(_document(), _document()))


def test_unknown_license_is_rejected() -> None:
    with pytest.raises(ValidationError, match="Unknown license"):
        CorpusManifest.model_validate(_manifest(_document(license="missing")))


@pytest.mark.parametrize(
    "overrides",
    [
        {"sha256": "abc"},
        {"doc_id": "Not A Slug"},
        {"identifiers": {}},
        {"published": "July 2024"},
        {"legal_status": "advisory"},
        {"unexpected_field": "x"},
    ],
)
def test_invalid_document_is_rejected(overrides: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        CorpusManifest.model_validate(_manifest(_document(**overrides)))


def test_eu_regulation_fits_the_schema() -> None:
    """Phase 2 readiness: a binding EU regulation needs no schema change. Synthetic values."""
    regulation = _document(
        doc_id="eu-regulation-example",
        corpus_id="eu-ai-act",
        document_type="regulation",
        jurisdiction="EU",
        legal_status="binding",
        identifiers={"celex": "32024R1689", "eli": "http://data.europa.eu/eli/reg/2024/1689/oj"},
        published="2024-07-12",
    )
    manifest = CorpusManifest.model_validate(_manifest(_document(), regulation))

    doc = manifest.documents[1]
    assert doc.document_type is DocumentType.REGULATION
    assert doc.legal_status is LegalStatus.BINDING

    chunk = ChunkMetadata(
        doc_id=doc.doc_id,
        chunk_id="art-9-par-2",
        section_path=["Chapter III", "Section 2", "Article 9", "Paragraph 2"],
        structural_unit=StructuralUnit.PARAGRAPH,
        page_start=10,
        page_end=10,
    )
    assert chunk.section_path[-2] == "Article 9"


def test_nist_chunk_metadata() -> None:
    chunk = ChunkMetadata(
        doc_id="nist-ai-100-1",
        chunk_id="govern-1-1",
        section_path=["GOVERN", "GOVERN 1", "GOVERN 1.1"],
        structural_unit=StructuralUnit.SUBCATEGORY,
        page_start=22,
        page_end=22,
    )
    assert chunk.structural_unit is StructuralUnit.SUBCATEGORY


def test_chunk_page_range_must_be_ordered() -> None:
    with pytest.raises(ValidationError, match="page_end"):
        ChunkMetadata(
            doc_id="doc-a",
            chunk_id="c1",
            section_path=["1"],
            structural_unit=StructuralUnit.SECTION,
            page_start=5,
            page_end=4,
        )
