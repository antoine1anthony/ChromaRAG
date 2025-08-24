"""Helper utilities used across the API."""

from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
from typing import List, Dict
from models import Document
from security import encrypt_data

# Initialize the OpenCLIP embedding function
def get_openclip_embedding_function() -> OpenCLIPEmbeddingFunction:
    """Return the default OpenCLIP embedding function."""
    return OpenCLIPEmbeddingFunction()

# Initialize the ImageLoader for multimodal collections
def get_image_loader() -> ImageLoader:
    """Return the default image loader for multimodal content."""
    return ImageLoader()

# Build lists of document fields for ChromaDB operations. This helper ensures
# that all lists have the same length so calls to ``add`` and ``update`` do not
# fail due to mismatched inputs.
def build_chroma_fields(documents: List[Document]) -> Dict[str, List]:
    """Return field lists for a sequence of documents."""
    return {
        "ids": [doc.id for doc in documents],
        "documents": [doc.text for doc in documents],
        "metadatas": [
            encrypt_data(str(doc.metadata)) if doc.metadata else None
            for doc in documents
        ],
        "embeddings": [doc.embedding for doc in documents],
        "images": [doc.image for doc in documents],
        "uris": [doc.uri for doc in documents],
    }
