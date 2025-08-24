# API Documentation

This document describes the public REST API endpoints and utility functions available in **ChromaRAG**. The API is served using FastAPI and is secured using API key authentication.

## Authentication

All endpoints require a valid API key. Include the key in the `Authorization` header:

```bash
curl -H "Authorization: Bearer your-secure-api-key" http://localhost:8000
```

## Endpoints

### Collections

#### `POST /collections/create_collection`
Create a new ChromaDB collection.

**Parameters**
- `name` (*str*, required) – Name of the collection.
- `embedding_function` (*str*, optional) – Name of the embedding function to use.

**Example**
```bash
curl -X POST \
  -H "Authorization: Bearer your-secure-api-key" \
  -d "name=my_collection" \
  http://localhost:8000/collections/create_collection
```

#### `DELETE /collections/delete_collection/{collection_name}`
Delete an existing collection by name.

**Example**
```bash
curl -X DELETE \
  -H "Authorization: Bearer your-secure-api-key" \
  http://localhost:8000/collections/delete_collection/my_collection
```

### Documents

#### `POST /documents/add_documents_background/{collection_name}`
Add documents to a collection using a background task.

Body payload is a JSON array of `Document` objects.

**Example**
```bash
curl -X POST \
  -H "Authorization: Bearer your-secure-api-key" \
  -H "Content-Type: application/json" \
  -d '[{"id": "doc1", "text": "hello"}]' \
  http://localhost:8000/documents/add_documents_background/my_collection
```

#### `POST /documents/add_documents/{collection_name}`
Add documents to a multimodal collection synchronously.

Body payload is a JSON array of `Document` objects.

#### `POST /documents/query_collection/{collection_name}`
Query a collection using text, embeddings, images or URIs.

Body payload is a `Query` object.

#### `PUT /documents/update_documents/{collection_name}`
Update existing documents in a collection. The body payload is a JSON array of `Document` objects. Document IDs must already exist.

## Data Models

### `Document`
```json
{
  "id": "unique-id",
  "text": "optional text",
  "metadata": {"key": "value"},
  "embedding": [0.0, 0.1, ...],
  "image": null,
  "uri": null
}
```

### `Query`
```json
{
  "query_texts": ["search term"],
  "query_embeddings": [[0.0, 0.1, ...]],
  "query_images": null,
  "query_uris": null,
  "n_results": 10,
  "where": null,
  "where_document": null
}
```

## Utility Functions

The project exposes helper functions that can be imported for programmatic use:

- `get_openclip_embedding_function()` – returns an OpenCLIP embedding function instance.
- `get_image_loader()` – returns an image loader for multimodal inputs.
- `build_chroma_fields(documents)` – converts a list of `Document` models into field lists for ChromaDB operations.
- `encrypt_data(data)` / `decrypt_data(data)` – utilities for encrypting and decrypting strings.
- `anonymize_data(data)` – one-way hashing of sensitive values.

## Usage Example

Below is a small Python example that creates a collection and inserts a document:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
headers = {"Authorization": "Bearer your-secure-api-key"}

# Create the collection
client.post("/collections/create_collection", params={"name": "demo"}, headers=headers)

# Add a document
payload = [{"id": "doc1", "text": "hello world"}]
client.post("/documents/add_documents/demo", json=payload, headers=headers)
```

This example uses `TestClient` for convenience but any HTTP client can be used.
