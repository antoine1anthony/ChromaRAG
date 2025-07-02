"""Endpoints for managing ChromaDB collections."""

from fastapi import APIRouter, HTTPException
from typing import Optional
from chroma_client import get_client

router = APIRouter()

@router.post("/create_collection")
async def create_collection(name: str, embedding_function: Optional[str] = None):
    """Create a new collection."""
    try:
        client = get_client()
        client.create_collection(name=name, embedding_function=embedding_function)
        return {"message": f"Collection {name} created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_collection/{collection_name}")
async def delete_collection(collection_name: str):
    """Remove an existing collection."""
    try:
        client = get_client()
        client.delete_collection(name=collection_name)
        return {"message": f"Collection {collection_name} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

