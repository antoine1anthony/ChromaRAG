"""Utility for creating and reusing the ChromaDB client."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional
from urllib.parse import urlparse

import chromadb


def _build_http_client(database_url: str) -> chromadb.ClientAPI:
    """Return an :class:`chromadb.HttpClient` configured for ``database_url``."""

    parsed = urlparse(database_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(
            "DATABASE_URL must be an HTTP(S) URL when provided."
        )

    host = parsed.hostname or "localhost"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    ssl = parsed.scheme == "https"

    return chromadb.HttpClient(host=host, port=port, ssl=ssl)


def _build_persistent_client(path: Optional[str] = None) -> chromadb.PersistentClient:
    """Return a :class:`chromadb.PersistentClient` for local persistence."""

    client_path = path or os.getenv("CHROMA_PERSIST_PATH", "./data/chromadb")
    return chromadb.PersistentClient(path=client_path)


@lru_cache(maxsize=1)
def get_client() -> chromadb.ClientAPI:
    """Return a shared ChromaDB client instance."""

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return _build_http_client(database_url)

    return _build_persistent_client()
