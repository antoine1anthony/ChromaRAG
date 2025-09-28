"""Persistence layer for storing processed documents and embeddings in Postgres."""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Iterable, Iterator, Optional

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    create_engine,
    delete,
    func,
    text as sql_text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector

from app.models import Document

_LOGGER = logging.getLogger(__name__)


def _determine_embedding_dimension() -> int:
    """Return the configured embedding dimension, defaulting sensibly."""

    value = os.getenv("EMBEDDING_DIM")
    if value:
        try:
            dimension = int(value)
            if dimension > 0:
                return dimension
            _LOGGER.warning(
                "EMBEDDING_DIM must be positive; received %s. Falling back to 1536.",
                value,
            )
        except ValueError:
            _LOGGER.warning(
                "Invalid EMBEDDING_DIM value '%s'; falling back to 1536.", value
            )
    return 1536


EMBEDDING_DIMENSION = _determine_embedding_dimension()

Base = declarative_base()


class ProcessedDocument(Base):
    """ORM model storing pre-processed data and embedding backups."""

    __tablename__ = "processed_documents"

    id = Column(String, primary_key=True)
    collection_name = Column(String, nullable=False, index=True)
    text = Column(Text, nullable=True)
    preprocessed_text = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True)
    metadata_labels = Column(JSONB, nullable=True)
    embedding = Column(Vector(EMBEDDING_DIMENSION), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


_ENGINE = None
_SESSION_FACTORY: Optional[sessionmaker] = None
_INITIALISED = False


def _get_database_url() -> Optional[str]:
    return os.getenv("POSTGRES_URL")


def _get_engine():
    global _ENGINE, _SESSION_FACTORY
    if _ENGINE is not None:
        return _ENGINE

    database_url = _get_database_url()
    if not database_url:
        _LOGGER.info("POSTGRES_URL is not set; Postgres persistence disabled.")
        return None

    _ENGINE = create_engine(database_url, pool_pre_ping=True, future=True)
    _SESSION_FACTORY = sessionmaker(bind=_ENGINE, autoflush=False, future=True)
    return _ENGINE


def init_db() -> None:
    """Initialise the Postgres schema and pgvector extension if configured."""

    global _INITIALISED
    if _INITIALISED:
        return

    engine = _get_engine()
    if engine is None:
        return

    try:
        with engine.begin() as connection:
            connection.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(bind=engine)
        _INITIALISED = True
    except SQLAlchemyError as exc:
        _LOGGER.error("Failed to initialise Postgres storage: %s", exc)


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""

    if _SESSION_FACTORY is None and _get_engine() is None:
        raise RuntimeError("Postgres session requested but POSTGRES_URL is not configured.")

    session = _SESSION_FACTORY()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as exc:
        session.rollback()
        _LOGGER.error("Postgres operation failed: %s", exc)
        raise
    finally:
        session.close()


def _preprocess_text(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    return " ".join(text.split()).lower()


def store_processed_documents(collection_name: str, documents: Iterable[Document]) -> None:
    """Persist processed document data and embeddings for backup."""

    init_db()
    if _SESSION_FACTORY is None:
        return

    with get_session() as session:
        for document in documents:
            embedding = None
            if document.embedding is not None:
                embedding_values = list(document.embedding)
                if len(embedding_values) != EMBEDDING_DIMENSION:
                    _LOGGER.warning(
                        (
                            "Document %s embedding has %d dimensions; expected %d. "
                            "Embedding will be omitted from Postgres backup."
                        ),
                        document.id,
                        len(embedding_values),
                        EMBEDDING_DIMENSION,
                    )
                else:
                    embedding = embedding_values
            values = {
                "collection_name": collection_name,
                "text": document.text,
                "preprocessed_text": _preprocess_text(document.text),
                "metadata": document.metadata,
                "metadata_labels": sorted(document.metadata.keys()) if document.metadata else None,
                "embedding": embedding,
            }
            existing = session.get(ProcessedDocument, document.id)
            if existing:
                for field, value in values.items():
                    setattr(existing, field, value)
            else:
                session.add(ProcessedDocument(id=document.id, **values))


def remove_collection(collection_name: str) -> None:
    """Delete all backups for ``collection_name``."""

    init_db()
    if _SESSION_FACTORY is None:
        return

    with get_session() as session:
        session.execute(
            delete(ProcessedDocument).where(ProcessedDocument.collection_name == collection_name)
        )

