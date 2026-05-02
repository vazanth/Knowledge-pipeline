from chromadb import PersistentClient
import asyncio


class VectorStore:
    def __init__(self, chroma_db_path):
        self.chroma_db_path = chroma_db_path
        self.client = PersistentClient(path=chroma_db_path)
        self.collection = self.client.get_or_create_collection(name="research_docs")

    async def upsert_collection(self, id, document):
        try:
            await asyncio.to_thread(self.collection.upsert, ids=id, documents=document)
        except:
            raise


# def index_document(file_path):
#     text = read_file(file_path)
#     text = remove_frontmatter(text)

#     chunks = chunk_text(text)
#     embeddings = get_embeddings(chunks)

#     store_in_chroma(chunks, embeddings, file_path)
