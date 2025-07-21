from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional, Annotated
import numpy as np

class Document(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    
    id: str = Field(..., description="Unique identifier for the document")
    text: Optional[str] = Field(None, description="Text content of the document")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")
    embedding: Optional[List[float]] = Field(
        None, description="Precomputed embedding vector"
    )
    image: Optional[np.ndarray] = Field(None, description="Image data as a numpy array")
    uri: Optional[HttpUrl] = Field(None, description="Valid URI to the external data source")

class Query(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    
    query_texts: Optional[List[str]] = Field(None, description="List of query texts")
    query_embeddings: Optional[List[List[float]]] = Field(
        None, description="List of embedding vectors"
    )
    query_images: Optional[List[np.ndarray]] = Field(None, description="List of images as numpy arrays")
    query_uris: Optional[List[HttpUrl]] = Field(None, description="List of valid URIs to external data sources")
    n_results: int = Field(10, description="Number of results to return")
    where: Optional[Dict] = Field(None, description="Filter conditions based on metadata")
    where_document: Optional[Dict] = Field(None, description="Filter conditions based on document content")