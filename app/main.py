"""Application entry point for the FastAPI server.

This module creates the :class:`FastAPI` instance, adds middleware and includes
all API routers. Import ``app`` from this module when running with Uvicorn or
for testing.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import collections, documents
from app.dependencies import get_api_key
from app.middleware import RateLimitMiddleware

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware, max_request=10, time_window=60)

# Include the routers with API key dependency
app.include_router(collections.router, prefix="/collections", tags=["Collections"], dependencies=[Depends(get_api_key)])
app.include_router(documents.router, prefix="/documents", tags=["Documents"], dependencies=[Depends(get_api_key)])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
