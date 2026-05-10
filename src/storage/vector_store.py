import asyncio
from chromadb import PersistentClient


class VectorStore:
    def __init__(self, chroma_db_path):
        self.client = PersistentClient(path=chroma_db_path)

    def get_collection(self, name: str):
        return self.client.get_or_create_collection(name=name)

    async def upsert(self, collection_name, ids, documents, embeddings, metadatas=None):
        collection = self.get_collection(collection_name)

        await asyncio.to_thread(
            collection.upsert,
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
