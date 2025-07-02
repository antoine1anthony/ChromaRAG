"""Application entry point for the FastAPI server.

This module creates the :class:`FastAPI` instance, adds middleware and includes
all API routers. Import ``app`` from this module when running with Uvicorn or
for testing.
"""

from fastapi import FastAPI, Depends
from routers import collections, documents
from dependencies import get_api_key
from middleware import RateLimitMiddleware

# Initialize the FastAPI app
app = FastAPI()
app.add_middleware(RateLimitMiddleware, max_requests=10, time_window=60)

# Include the routers with API key dependency
app.include_router(collections.router, prefix="/collections", tags=["Collections"], dependencies=[Depends(get_api_key)])
app.include_router(documents.router, prefix="/documents", tags=["Documents"], dependencies=[Depends(get_api_key)])
