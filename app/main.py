from fastapi import FastAPI, Depends
from routers import collections, documents
from dependencies import get_api_key
from middleware import RateLimitMiddleware

# Initialize the FastAPI app
app = FastAPI(
    title="ChromaRAG API",
    description="A Retrieval-Augmented Generation (RAG) pipeline with multimodal data support",
    version="1.0.0"
)
app.add_middleware(RateLimitMiddleware, max_request=10, time_window=60)

# Health check endpoint (no authentication required)
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring services"""
    return {"status": "healthy", "service": "ChromaRAG API"}

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": "Welcome to ChromaRAG API",
        "docs": "/docs",
        "health": "/health"
    }

# Include the routers with API key dependency
app.include_router(collections.router, prefix="/collections", tags=["Collections"], dependencies=[Depends(get_api_key)])
app.include_router(documents.router, prefix="/documents", tags=["Documents"], dependencies=[Depends(get_api_key)])
