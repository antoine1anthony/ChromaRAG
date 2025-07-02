"""Utility for creating and reusing the ChromaDB client."""

import chromadb

# Initialize the ChromaDB Persistent Client
client = chromadb.PersistentClient(path="/data/chromadb")

def get_client() -> chromadb.PersistentClient:
    """Return the shared :class:`chromadb.PersistentClient` instance."""
    return client
