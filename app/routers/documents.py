"""Endpoints for managing documents within collections."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from app.chroma_client import get_client
from app.models import Document, Query
from app.utils import (
    build_chroma_fields,
    get_image_loader,
    get_openclip_embedding_function,
)
from app.postgres_store import store_processed_documents
from app.security import decrypt_data
import logging
from datetime import datetime
from app.metadata_enrichment import enrich_metadata, is_metadata_complete

# Configure the logging
logging.basicConfig(filename='audit.log', level=logging.INFO)

def log_access(user: str, action: str, document_id: str) -> None:
    """Write an audit log entry for document operations."""
    logging.info(f"{datetime.utcnow()} - {user} performed {action} on document ID {document_id}")

router = APIRouter()

# Add documents to a collection (supports text-only)
@router.post("/add_documents_background/{collection_name}")
async def add_documents_background(
    collection_name: str, documents: List[Document], background_tasks: BackgroundTasks
):
    """Schedule a background task to add documents to a collection."""
    background_tasks.add_task(add_documents_task, collection_name, documents)
    return {"message": "Documents are being added in the background."}

async def add_documents_task(collection_name: str, documents: List[Document]):
    """Background worker that inserts documents into ``collection_name``."""
    client = get_client()
    collection = client.get_or_create_collection(name=collection_name)

    for document in documents:
        if not is_metadata_complete(document.metadata):
            document.metadata = enrich_metadata(document)

    # Ensure that every field list has the same length as ``documents`` to
    # avoid errors in ChromaDB operations.
    fields = build_chroma_fields(documents)
    collection.add(**fields)
    store_processed_documents(collection_name, documents)

# Add documents to a collection (supports multimodal)
@router.post("/add_documents/{collection_name}")
async def add_documents(collection_name: str, documents: List[Document]):
    """Synchronously add documents to a multimodal collection."""
    try:
        client = get_client()
        embedding_function = get_openclip_embedding_function()
        data_loader = get_image_loader()
        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            data_loader=data_loader
        )

        for document in documents:
            if not is_metadata_complete(document.metadata):
                document.metadata = enrich_metadata(document)

        # Store all fields with consistent lengths to avoid errors
        fields = build_chroma_fields(documents)
        collection.add(**fields)
        store_processed_documents(collection_name, documents)
        return {"message": "Documents added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Query the collection (supports multimodal)
@router.post("/query_collection/{collection_name}")
async def query_collection(collection_name: str, query: Query):
    """Search a collection using text, embeddings, images or URIs."""
    try:
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
            include=["documents", "metadatas", "embeddings", "distances"]
        )

        # Decrypt the metadata before returning
        if results.get("metadatas"):
            results["metadatas"] = [
                [
                    decrypt_data(metadata)
                    if metadata is not None
                    else None
                    for metadata in metadata_list
                ]
                for metadata_list in results["metadatas"]
            ]

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update documents in a collection with consistency check (supports multimodal)
@router.put("/update_documents/{collection_name}")
async def update_documents(collection_name: str, documents: List[Document]):
    """Update existing documents, ensuring each ID already exists."""
    try:
        client = get_client()
        collection = client.get_collection(name=collection_name)

        # Check if all document IDs exist before updating
        existing_ids = collection.get(ids=[doc.id for doc in documents])['ids']
        if len(existing_ids) != len(documents):
            raise HTTPException(status_code=400, detail="Some document IDs do not exist")

        # Build field lists for the update, ensuring consistent lengths
        fields = build_chroma_fields(documents)
        collection.update(**fields)
        store_processed_documents(collection_name, documents)

        # Log the update action for SOC 2 compliance
        for doc in documents:
            log_access(user="example_user", action="update", document_id=doc.id)

        return {"message": "Documents updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
