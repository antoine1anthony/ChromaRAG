
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
│   └── middleware.py      # Middleware for rate limiting
├── Dockerfile             # Dockerfile for the FastAPI app
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
└── README.md              # Project overview and documentation
```

## Installation

### Local Development

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/g3ntl3Giants/ChromaRAG.git
    cd ChromaRAG
    ```

2. **Setup Docker**:
    ```bash
    docker-compose up --build
    ```

3. **Access the API**:
    - The API will be available at `http://localhost:8000`.
    - Swagger UI is available at `http://localhost:8000/docs`.

### Deploy to Render.com

ChromaRAG is configured for easy deployment on Render.com using the included `render.yaml` configuration file.

#### Prerequisites
- A [Render.com](https://render.com) account
- Your code pushed to a GitHub repository

#### Deployment Steps

1. **Connect to Render**:
   - Fork or push this repository to GitHub
   - Connect your GitHub account to Render.com
   - Create a new "Blueprint" service in Render

2. **Configure Environment Variables**:
   - Copy `.env.example` to `.env` and configure your values
   - In Render dashboard, set the following environment variables:
     - `API_KEY`: Your secure API key for authentication
     - `SECRET_KEY`: Secret key for JWT tokens
     - `ENVIRONMENT`: Set to "production"
   
3. **Deploy**:
   - Select your repository and the `render-deployment-support` branch
   - Render will automatically detect the `render.yaml` file
   - Click "Apply" to deploy

4. **Access Your Deployed API**:
   - Your API will be available at `https://your-service-name.onrender.com`
   - Swagger UI will be at `https://your-service-name.onrender.com/docs`

#### Render Configuration Details

The `render.yaml` file includes:
- **Web Service**: FastAPI application with Docker runtime
- **Database**: Optional PostgreSQL service for production use
- **Auto-scaling**: 1-3 instances based on traffic
- **Health checks**: Monitors `/docs` endpoint
- **Environment**: Production-ready configuration

## Authentication

The API is secured using API keys. Include the API key in the `Authorization` header as follows:

```bash
curl -H "Authorization: Bearer your-secure-api-key" http://localhost:8000/your-endpoint
```

## Data Encryption

Sensitive data is encrypted and anonymized using the cryptography library to ensure data protection. Refer to `app/security.py` for implementation details.

## Contributing


Feel free to contribute by submitting a pull request. Ensure that your code adheres to the project's coding standards.

## License

TBA
