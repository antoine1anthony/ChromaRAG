from fastapi import APIRouter, HTTPException
from typing import Optional
from app.chroma_client import get_client

router = APIRouter()

# Create a collection
@router.post("/create_collection")
async def create_collection(name: str, embedding_function: Optional[str] = None):
    try:
        client = get_client()
        collection = client.create_collection(name=name, embedding_function=embedding_function)
        return {"message": f"Collection {name} created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete a collection
@router.delete("/delete_collection/{collection_name}")
async def delete_collection(collection_name: str):
    try:
        client = get_client()
        client.delete_collection(name=collection_name)
        return {"message": f"Collection {collection_name} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

