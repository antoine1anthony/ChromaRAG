from typing import List, Optional
import json
from mcp.server.fastmcp import FastMCP

from app.chroma_client import get_client
from app.security import encrypt_data, decrypt_data


mcp = FastMCP("ChromaRAG")


def get_user_role() -> str:
    """Return the role for the current request.

    This placeholder assumes every request comes from an admin.
    In the future, this will be replaced with logic from the auth module.
    """

    return "admin"


def filter_collections_by_role(collections: List[str], role: str) -> List[str]:
    """Filter collections based on the provided role."""

    if role == "admin":
        return collections

    # TODO: Implement proper role-based collection access control
    # Currently, non-admin users cannot access any collections due to empty allowed list
    # Future implementation should:
    # - Define role-to-collection mappings in configuration or database
    # - Support user-specific collection permissions
    # - Allow granular access control (read/write permissions)
    allowed: List[str] = []
    return [c for c in collections if c in allowed]


@mcp.tool()
def create_collection(name: str) -> str:
    """Create a new collection."""
    if not name or not isinstance(name, str):
        raise ValueError("The collection name must be a non-empty string.")
    client = get_client()
    client.create_collection(name=name)
    return f"Collection {name} created"


@mcp.tool()
def delete_collection(name: str) -> str:
    """Delete a collection."""
    if not name or not isinstance(name, str):
        raise ValueError("The collection name must be a non-empty string.")
    client = get_client()
    client.delete_collection(name=name)
    return f"Collection {name} deleted"


@mcp.tool()
def add_document(collection_name: str, document_id: str, text: Optional[str] = None, metadata: Optional[dict] = None) -> str:
    """Add a single document to a collection."""
    if not document_id:
        raise ValueError("Document ID cannot be None or empty string.")
    client = get_client()
    collection = client.get_or_create_collection(name=collection_name)

    encrypted_metadata = None if not metadata else encrypt_data(json.dumps(metadata))

    collection.add(
        ids=[document_id],
        documents=[text] if text else None,
        metadatas=[encrypted_metadata] if encrypted_metadata else None,
        embeddings=None,
        images=None,
        uris=None,
    )
    return "Document added"


@mcp.tool()
def query_collection(collection_name: str, query_texts: Optional[List[str]] = None, n_results: int = 10) -> dict:
    """Query a collection."""
    if not collection_name:
        raise ValueError("The collection_name must be a non-empty string.")
    client = get_client()
    collection = client.get_collection(name=collection_name)
    results = collection.query(
        query_texts=query_texts,
        query_embeddings=None,
        query_images=None,
        query_uris=None,
        n_results=n_results,
        where=None,
        where_document=None,
        include=["documents", "metadatas", "embeddings", "distances"],
    )
    results["metadatas"] = [
        json.loads(decrypt_data(m)) if m is not None else None for m in results.get("metadatas", [])
    ]
    return results


@mcp.resource("chroma://collections")
def list_collections() -> List[str]:
    """List existing collection names."""
    client = get_client()
    cols = client.list_collections()
    all_collections = [c.name if hasattr(c, "name") else c for c in cols]
    role = get_user_role()
    return filter_collections_by_role(all_collections, role)


if __name__ == "__main__":
    mcp.run()

