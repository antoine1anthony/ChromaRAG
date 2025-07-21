from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from app.chroma_client import get_client
from app.models import Document, Query
from app.utils import get_openclip_embedding_function, get_image_loader
from app.security import encrypt_data, decrypt_data
import logging
from datetime import datetime

# Configure the logging
logging.basicConfig(filename='audit.log', level=logging.INFO)

def log_access(user: str, action: str, document_id: str):
    logging.info(f"{datetime.utcnow()} - {user} performed {action} on document ID {document_id}")

router = APIRouter()

# Add documents to a collection (supports text-only)
@router.post("/add_documents_background/{collection_name}")
async def add_documents_background(
    collection_name: str, documents: List[Document], background_tasks: BackgroundTasks
):
    background_tasks.add_task(add_documents_task, collection_name, documents)
    return {"message": "Documents are being added in the background."}

async def add_documents_task(collection_name: str, documents: List[Document]):
    client = get_client()
    collection = client.get_or_create_collection(name=collection_name)
    
    # Encrypt metadata before storing
    encrypted_metadata = [encrypt_data(str(doc.metadata)) for doc in documents if doc.metadata]

    collection.add(
        ids=[doc.id for doc in documents],
        documents=[doc.text for doc in documents if doc.text],
        metadatas=encrypted_metadata,
        embeddings=[doc.embedding for doc in documents if doc.embedding],
        images=[doc.image for doc in documents if doc.image],
        uris=[doc.uri for doc in documents if doc.uri]
    )

# Add documents to a collection (supports multimodal)
@router.post("/add_documents/{collection_name}")
async def add_documents(collection_name: str, documents: List[Document]):
    try:
        client = get_client()
        embedding_function = get_openclip_embedding_function()
        data_loader = get_image_loader()
        collection = client.get_or_create_collection(
            name=collection_name, 
            embedding_function=embedding_function, 
            data_loader=data_loader
        )

        # Encrypt metadata before storing
        encrypted_metadata = [encrypt_data(str(doc.metadata)) for doc in documents if doc.metadata]

        collection.add(
            ids=[doc.id for doc in documents],
            documents=[doc.text for doc in documents if doc.text],
            metadatas=encrypted_metadata,
            embeddings=[doc.embedding for doc in documents if doc.embedding],
            images=[doc.image for doc in documents if doc.image],
            uris=[doc.uri for doc in documents if doc.uri]
        )
        return {"message": "Documents added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Query the collection (supports multimodal)
@router.post("/query_collection/{collection_name}")
async def query_collection(collection_name: str, query: Query):
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
            include=["documents", "metadatas", "embeddings", "distances"]  # Customize this as needed
        )

        # Decrypt the metadata before returning
        decrypted_metadata = [
            decrypt_data(metadata) 
            for metadata in results['metadatas']
        ]
        results['metadatas'] = decrypted_metadata

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update documents in a collection with consistency check (supports multimodal)
@router.put("/update_documents/{collection_name}")
async def update_documents(collection_name: str, documents: List[Document]):
    try:
        client = get_client()
        collection = client.get_collection(name=collection_name)

        # Check if all document IDs exist before updating
        existing_ids = collection.get(ids=[doc.id for doc in documents])['ids']
        if len(existing_ids) != len(documents):
            raise HTTPException(status_code=400, detail="Some document IDs do not exist")

        # Decrypt the existing metadata before performing updates
        existing_metadata = [
            decrypt_data(metadata) 
            for metadata in collection.get(ids=existing_ids)['metadatas']
        ]

        # Encrypt the new metadata before updating
        encrypted_metadata = [
            encrypt_data(str(doc.metadata)) for doc in documents if doc.metadata
        ]

        collection.update(
            ids=[doc.id for doc in documents],
            documents=[doc.text for doc in documents if doc.text],
            metadatas=encrypted_metadata,
            embeddings=[doc.embedding for doc in documents if doc.embedding],
            images=[doc.image for doc in documents if doc.image]
        )

        # Log the update action for SOC 2 compliance
        for doc in documents:
            log_access(user="example_user", action="update", document_id=doc.id)

        return {"message": "Documents updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))