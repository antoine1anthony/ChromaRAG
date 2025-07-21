import chromadb

# Initialize the ChromaDB Persistent Client
client = chromadb.PersistentClient(path="./data/chromadb")

def get_client():
    return client
