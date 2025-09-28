from pathlib import Path

from pypdf import PdfWriter

from app.metadata_enrichment import enrich_metadata, is_metadata_complete
from app.models import Document


def _create_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata(
        {
            "/Title": "Sample PDF",
            "/Author": "Jane Doe",
            "/Subject": "Demonstration",
            "/CreationDate": "D:20240101000000Z",
        }
    )
    with pdf_path.open("wb") as file:
        writer.write(file)
    return pdf_path


def test_enrich_metadata_extracts_pdf_fields(tmp_path):
    pdf_path = _create_pdf(tmp_path)
    document = Document(
        id="doc-1",
        text="This document describes compliance processes and audit readiness.",
        metadata={"file_path": str(pdf_path)},
    )

    metadata = enrich_metadata(document)

    assert metadata["title"] == "Sample PDF"
    assert metadata["author"] == "Jane Doe"
    assert metadata["subject"] == "Demonstration"
    assert metadata["created_at"].startswith("2024-01-01")
    assert "summary" in metadata and metadata["summary"]
    assert is_metadata_complete(metadata)


def test_enrich_metadata_generates_keywords_and_topics():
    text = (
        "Artificial intelligence streamlines compliance workflows. "
        "Natural language processing highlights regulatory obligations. "
        "Embedding backups ensure resilient retrieval operations."
    )
    document = Document(id="doc-2", text=text)

    metadata = enrich_metadata(document)

    assert metadata["summary"].startswith("Artificial intelligence streamlines")
    assert "artificial" in metadata["keywords"]
    assert isinstance(metadata["topics"], list) and metadata["topics"]
    assert metadata["topics"][0] in metadata["keywords"]


def test_enrich_metadata_overwrites_blank_fields():
    text = "Automation improves compliance posture and reduces manual review overhead."
    document = Document(
        id="doc-blank",
        text=text,
        metadata={"summary": "", "topics": [], "keywords": []},
    )

    metadata = enrich_metadata(document)

    assert metadata["summary"].startswith("Automation improves compliance posture")
    assert metadata["topics"]
    assert metadata["keywords"]
    assert is_metadata_complete(metadata)


def test_enrich_metadata_handles_llm_absence(monkeypatch):
    monkeypatch.setenv("METADATA_LLM_API_KEY", "test-key")
    document = Document(
        id="doc-3",
        text="Data governance policies guide secure document processing.",
    )

    metadata = enrich_metadata(document)

    assert metadata["summary"].startswith("Data governance policies")
    assert "governance" in metadata["keywords"]

    monkeypatch.delenv("METADATA_LLM_API_KEY")
