"""Utilities for enriching document metadata prior to persistence."""

from __future__ import annotations

import io
import json
import logging
import os
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import requests
from pypdf import PdfReader

from app.models import Document

_LOGGER = logging.getLogger(__name__)

_STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "this",
    "from",
    "have",
    "your",
    "into",
    "about",
    "there",
    "their",
    "will",
    "which",
    "while",
    "where",
    "been",
    "being",
    "over",
    "also",
    "such",
    "through",
    "shall",
    "should",
    "would",
    "could",
    "here",
    "when",
    "than",
    "then",
    "them",
    "they",
    "because",
    "between",
    "after",
    "before",
    "other",
    "more",
    "only",
    "those",
    "these",
    "into",
    "upon",
}

_REQUIRED_FIELDS = {"title", "summary", "topics", "keywords"}


def _has_value(value: Any) -> bool:
    """Return ``True`` when ``value`` should be considered populated."""

    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return bool(value)


def _generate_title(text: str) -> Optional[str]:
    """Create a fallback title when PDF metadata does not supply one."""

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    for sentence in sentences:
        if sentence:
            return sentence[:120].strip()
    words = text.strip().split()
    if not words:
        return None
    return " ".join(words[:8]).strip()


@dataclass
class EnrichmentResult:
    """Structured response from the enrichment pipeline."""

    metadata: Dict[str, Any]
    evidence: Iterable[str]


def is_metadata_complete(metadata: Optional[Dict[str, Any]]) -> bool:
    """Return ``True`` when metadata already contains the expected keys."""

    if not metadata:
        return False
    populated = {key for key, value in metadata.items() if _has_value(value)}
    return _REQUIRED_FIELDS.issubset(populated)


def enrich_metadata(document: Document) -> Dict[str, Any]:
    """Populate missing metadata fields by inspecting the PDF/text content."""

    metadata: Dict[str, Any] = dict(document.metadata or {})

    pdf_details = _extract_pdf_metadata(document, metadata)
    metadata.update({k: v for k, v in pdf_details.items() if _has_value(v)})

    text_content = document.text or pdf_details.get("sample_text") or ""
    if text_content and not _has_value(metadata.get("title")):
        fallback_title = _generate_title(text_content)
        if fallback_title:
            metadata["title"] = fallback_title
    nlp_details = _extract_nlp_features(text_content)

    for key, value in nlp_details.metadata.items():
        if not _has_value(metadata.get(key)) and _has_value(value):
            metadata[key] = value

    existing_evidence = metadata.get("evidence") or []
    if not isinstance(existing_evidence, list):
        existing_evidence = [existing_evidence]
    evidence = list(dict.fromkeys([*existing_evidence, *nlp_details.evidence]))
    if evidence:
        metadata["evidence"] = evidence

    llm_enrichment = _call_llm(metadata, text_content)
    for key, value in llm_enrichment.items():
        if _has_value(value) and not _has_value(metadata.get(key)):
            metadata[key] = value

    return metadata


def _extract_pdf_metadata(document: Document, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Read intrinsic PDF metadata when the document references a PDF."""

    source_path = metadata.get("file_path") or metadata.get("local_path")
    reader: Optional[PdfReader] = None
    sample_text: Optional[str] = None

    if source_path:
        path = Path(source_path)
        if path.exists() and path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
    elif document.uri and str(document.uri).lower().endswith(".pdf"):
        uri = str(document.uri)
        try:
            response = requests.get(uri, timeout=10)
            response.raise_for_status()
            reader = PdfReader(io.BytesIO(response.content))
        except Exception as exc:  # pragma: no cover - network failures are logged
            _LOGGER.warning("Failed to download PDF from %s: %s", uri, exc)

    if reader is None:
        return {}

    info = reader.metadata or {}
    details: Dict[str, Any] = {}

    title = getattr(info, "title", None) or info.get("/Title")
    author = getattr(info, "author", None) or info.get("/Author")
    subject = getattr(info, "subject", None) or info.get("/Subject")
    creation_date = getattr(info, "creation_date", None) or info.get("/CreationDate")

    if title:
        details["title"] = title.strip()
    if author:
        details["author"] = author.strip()
    if subject:
        details["subject"] = subject.strip()
    if creation_date:
        details["created_at"] = _normalise_pdf_date(creation_date)

    try:
        details["page_count"] = len(reader.pages)
    except Exception:  # pragma: no cover - defensive only
        pass

    try:
        if reader.pages:
            sample_text = (reader.pages[0].extract_text() or "").strip()
    except Exception:  # pragma: no cover - extract_text can fail for some PDFs
        sample_text = None

    if sample_text:
        details["sample_text"] = sample_text

    return details


def _normalise_pdf_date(raw_value: Any) -> Optional[str]:
    """Convert PDF date formats to ISO-8601 strings."""

    if isinstance(raw_value, datetime):
        return raw_value.isoformat()

    if isinstance(raw_value, str):
        value = raw_value.strip()
        # PDF dates are commonly formatted as D:YYYYMMDDHHmmSSOHH'mm'
        match = re.match(r"D:(\d{4})(\d{2})?(\d{2})?(\d{2})?(\d{2})?(\d{2})?", value)
        if match:
            year, month, day, hour, minute, second = match.groups(default="01")
            try:
                parsed = datetime(
                    int(year), int(month), int(day), int(hour), int(minute), int(second)
                )
                return parsed.isoformat()
            except ValueError:
                pass
        try:
            parsed = datetime.fromisoformat(value)
            return parsed.isoformat()
        except ValueError:
            return value
    return None


def _extract_nlp_features(text: str) -> EnrichmentResult:
    """Derive keywords, topics, and summaries from the document text."""

    if not text:
        return EnrichmentResult(metadata={}, evidence=[])

    tokens = re.findall(r"[A-Za-z][A-Za-z'-]+", text.lower())
    filtered_tokens = [token for token in tokens if token not in _STOPWORDS]
    counts = Counter(filtered_tokens)

    keywords = [token for token, _ in counts.most_common(5)]
    topics = keywords[:3]

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    evidence = [sentence.strip() for sentence in sentences[:3] if sentence.strip()]
    summary = " ".join(evidence[:2]).strip()

    metadata = {}
    if summary:
        metadata["summary"] = summary
    if topics:
        metadata["topics"] = topics
    if keywords:
        metadata["keywords"] = keywords

    return EnrichmentResult(metadata=metadata, evidence=evidence)


def _call_llm(metadata: Dict[str, Any], text: str) -> Dict[str, Any]:
    """Optionally call an LLM to enrich metadata when configured."""

    api_key = os.getenv("METADATA_LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    model = os.getenv("METADATA_LLM_MODEL", "gpt-4o-mini")

    if not api_key or not text:
        return {}

    try:
        from openai import OpenAI  # type: ignore
    except ImportError:  # pragma: no cover - optional dependency
        _LOGGER.info("openai package not installed; skipping LLM enrichment")
        return {}

    client = OpenAI(api_key=api_key)
    prompt = (
        "You are assisting with document metadata enrichment. Given the following text "
        "and existing metadata, provide a concise JSON object with optional keys "
        "'summary', 'topics', 'keywords', and 'labels'. Ensure the response is strictly "
        "valid JSON.\n\nMetadata: "
        f"{json.dumps(metadata, ensure_ascii=False)}\n\nText snippet:\n{text[:4000]}"
    )

    try:
        response = client.responses.create(
            model=model,
            input=[{"role": "user", "content": prompt}],
            temperature=0,
        )
    except Exception as exc:  # pragma: no cover - network failures are logged
        _LOGGER.warning("LLM enrichment failed: %s", exc)
        return {}

    try:
        content = response.output[0].content[0].text  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - shape differences across SDK versions
        try:
            content = response.output_text  # type: ignore[attr-defined]
        except Exception:
            _LOGGER.warning("LLM response format unexpected; skipping enrichment")
            return {}

    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        _LOGGER.warning("LLM returned non-JSON content; skipping enrichment")
    return {}


__all__ = ["enrich_metadata", "is_metadata_complete"]
