#!/bin/bash

# Start script for ChromaRAG on Render.com
# This script sets up the environment and starts the FastAPI application

set -e  # Exit on any error

echo "Starting ChromaRAG on Render.com..."

# Create data directory if it doesn't exist
mkdir -p /app/data/chromadb

# Set default environment variables if not provided
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}
export ENVIRONMENT=${ENVIRONMENT:-production}

# Start the FastAPI application
echo "Starting FastAPI server on $HOST:$PORT..."
exec uvicorn app.main:app --host $HOST --port $PORT --workers 1