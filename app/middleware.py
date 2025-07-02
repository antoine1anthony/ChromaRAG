"""Middleware components used by the FastAPI application."""

from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory IP based rate limiting middleware."""

    def __init__(self, app: FastAPI, max_requests: int, time_window: int):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next):
        """Process each request and enforce rate limits."""
        client_ip = request.client.host
        current_time = time.time()

        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []

        self.request_counts[client_ip] = [
            timestamp for timestamp in self.request_counts[client_ip]
            if timestamp > current_time - self.time_window
        ]

        if len(self.request_counts[client_ip]) >= self.max_requests:
            raise HTTPException(status_code=HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")

        self.request_counts[client_ip].append(current_time)
        response = await call_next(request)
        return response
