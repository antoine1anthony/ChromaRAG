"""Pydantic models used by the API."""

from pydantic import BaseModel, Field, HttpUrl, conlist
from typing import List, Dict, Optional
import numpy as np

class Document(BaseModel):
    """Represents a single item that can be stored in ChromaDB."""
    id: str = Field(..., description="Unique identifier for the document")
    text: Optional[str] = Field(None, description="Text content of the document")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")
    embedding: Optional[conlist(float, min_items=128, max_items=128)] = Field(
        None, description="Precomputed embedding vector of length 128"
    )
    image: Optional[np.ndarray] = Field(None, description="Image data as a numpy array")
    uri: Optional[HttpUrl] = Field(None, description="Valid URI to the external data source")

class Query(BaseModel):
    """Query parameters used when searching a collection."""
    query_texts: Optional[List[str]] = Field(None, description="List of query texts")
    query_embeddings: Optional[List[conlist(float, min_items=128, max_items=128)]] = Field(
        None, description="List of embedding vectors, each of length 128"
    )
    query_images: Optional[List[np.ndarray]] = Field(None, description="List of images as numpy arrays")
    query_uris: Optional[List[HttpUrl]] = Field(None, description="List of valid URIs to external data sources")
    n_results: int = Field(10, description="Number of results to return")
    where: Optional[Dict] = Field(None, description="Filter conditions based on metadata")
    where_document: Optional[Dict] = Field(None, description="Filter conditions based on document content")