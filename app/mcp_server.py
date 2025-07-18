from typing import List, Optional
import json
from mcp.server.fastmcp import FastMCP

from chroma_client import get_client
from models import Document, Query
from security import encrypt_data, decrypt_data


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
def add_document(collection_name: str, document: Document) -> str:
    """Add a single document to a collection."""
    if not document.id:
        raise ValueError("The document must have a valid 'id' that is not None or empty.")
    client = get_client()
    collection = client.get_or_create_collection(name=collection_name)

    metadata = None if not document.metadata else encrypt_data(json.dumps(document.metadata))

    collection.add(
        ids=[document.id],
        documents=[document.text] if document.text else None,
        metadatas=[metadata] if metadata else None,
        embeddings=[document.embedding] if document.embedding else None,
        images=[document.image] if document.image is not None else None,
        uris=[document.uri] if document.uri else None,
    )
    return "Document added"


@mcp.tool()
def query_collection(collection_name: str, query: Query) -> dict:
    """Query a collection."""
    client = get_client()
    collection = client.get_collection(name=collection_name)
    results = collection.query(
        query_texts=query.query_texts,
        query_embeddings=query.query_embeddings,
        query_images=query.query_images,
        query_uris=query.query_uris,
        n_results=query.n_results,
        where=query.where,
        where_document=query.where_document,
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

