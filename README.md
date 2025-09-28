
# ChromaRAG

## Overview

ChromaRAG is a Retrieval-Augmented Generation (RAG) pipeline that supports multimodal data inputs, such as text, images, and URIs. It is built using FastAPI, ChromaDB, and Docker, with features for API key-based authentication, data validation, background processing, and rate limiting.

## Compliance

I will be seeking to ensure that ChromaRAG complies with GDPR, HIPAA, and SOC 2 standards. Achieving these certifications will require significant work to implement the necessary security controls, data management practices, and documentation.


## Features

- **Multimodal Data Support**: Handles text, images, and URIs in the same embedding space.
- **Swagger/OpenAPI Documentation**: Automatically generated interactive API docs.
- **API Key-based Authentication**: Secures endpoints using API keys.
- **Data Validation**: Ensures data integrity with strict validation rules.
- **Consistency Checks**: Verifies data consistency before updates or deletes.
- **Background Processing**: Offloads time-consuming tasks to background processes.
- **Rate Limiting**: Prevents overloading the API with excessive requests.
- **Vector Backups in Postgres**: Mirrors documents, metadata labels, and embeddings inside a pgvector-enabled Postgres database for recovery and analytics workflows.
- **Compliance**: Implements data encryption, anonymization, and access controls for GDPR, HIPAA, and SOC 2 compliance.

## Folder Structure

```
ChromaRAG/
├── app/
│   ├── main.py            # FastAPI application
│   ├── models.py          # Pydantic models
│   ├── chroma_client.py   # ChromaDB client setup and utilities
│   ├── dependencies.py    # Dependency handling for API key authentication
│   ├── routers/
│   │   ├── __init__.py    # Router initialization
│   │   ├── collections.py # Endpoints related to collections
│   │   └── documents.py   # Endpoints related to documents
│   ├── utils.py           # Utility functions, e.g., embedding functions
│   ├── security.py        # Security functions for encryption and anonymization
│   ├── middleware.py      # Middleware for rate limiting
│   └── mcp_server.py      # MCP server exposing Chroma tools
├── Dockerfile             # Dockerfile for the FastAPI app
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
└── README.md              # Project overview and documentation
```

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/g3ntl3Giants/ChromaRAG.git
    cd ChromaRAG
    ```

2. **Setup Docker**:
    ```bash
    docker-compose up --build
    ```
    This starts FastAPI, ChromaDB, and a pgvector-enabled Postgres instance for embedding backups. The FastAPI container automatically persists documents and embeddings into both ChromaDB and Postgres when `POSTGRES_URL` is provided.

3. **Access the API**:
    - The API will be available at `http://localhost:8000`.
    - Swagger UI is available at `http://localhost:8000/docs`.
    - Additional endpoint documentation can be found in [docs/API.md](docs/API.md).

## MCP Server

This project includes an MCP server that exposes collection tools via the
Model Context Protocol. You can run it with:

```bash
uv run mcp dev app/mcp_server.py
```

Clients compatible with MCP can then connect to interact with your
collections and documents programmatically.

## Authentication

The API is secured using API keys. Include the API key in the `Authorization` header as follows:

```bash
curl -H "Authorization: Bearer your-secure-api-key" http://localhost:8000/your-endpoint
```

## Data Encryption

Sensitive data is encrypted and anonymized using the cryptography library to ensure data protection. Refer to `app/security.py` for implementation details.

## Render Deployment

Deploy the full stack on Render using the provided [`render.yaml`](render.yaml) blueprint:

```bash
render blueprint deploy render.yaml
```

The blueprint provisions:

- A FastAPI web service built from this repository's Dockerfile.
- A private Chromadb service with persistent disk storage.
- A managed Postgres instance with the pgvector extension for embedding backups.

## Kubernetes Deployment

The [`k8s/`](k8s) directory contains manifests for a production-style cluster deployment:

1. Create secrets for Postgres credentials by copying and editing `k8s/secrets.example.yaml` before applying manifests.
2. Apply the namespace, config maps, secrets, and workloads:

    ```bash
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/secrets.yaml   # your customized secret file
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/postgres.yaml
    kubectl apply -f k8s/chromadb.yaml
    kubectl apply -f k8s/api.yaml
    ```

3. Build and push the FastAPI container image referenced in `k8s/api.yaml` (replace `your-registry/chromarag:latest` with your published image).

The deployment keeps embeddings synchronized across ChromaDB and Postgres through the application's startup hooks and request handlers.

## Contributing


Feel free to contribute by submitting a pull request. Ensure that your code adheres to the project's coding standards.

## License

TBA
