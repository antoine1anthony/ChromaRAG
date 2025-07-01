from fastapi import FastAPI, Depends
from routers import collections, documents
from dependencies import get_api_key
from middleware import RateLimitMiddleware

# Initialize the FastAPI app
app = FastAPI()
# The middleware expects the argument name ``max_requests`` but ``max_request``
# was used previously which caused FastAPI to fail during startup. Use the
# correct argument name so the rate limiter initializes properly.
app.add_middleware(RateLimitMiddleware, max_requests=10, time_window=60)

# Include the routers with API key dependency
app.include_router(collections.router, prefix="/collections", tags=["Collections"], dependencies=[Depends(get_api_key)])
app.include_router(documents.router, prefix="/documents", tags=["Documents"], dependencies=[Depends(get_api_key)])
