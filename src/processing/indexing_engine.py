import asyncio
import os
from pathlib import Path
import requests
import yaml
import re
from processing.chunk import get_chunks


class IndexingEngine:

    def __init__(self, vector_store, embedding_model="default"):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    async def index_file(self, file_path):
        text = self.read_file(file_path)
        metadata, text = self.extract_frontmatter(text)

        for key, value in metadata.items():
            if isinstance(value, list):
                metadata[key] = ", ".join(value)

        chunks = get_chunks(text, "markdown")

        ids = [f"{Path(file_path).name}_{i}" for i in range(len(chunks))]

        chunk_metadatas = [metadata for _ in chunks]

        embeddings = await self.get_embeddings(chunks)

        await self.vector_store.upsert(
            "EmbeddingGemma", ids, chunks, embeddings, chunk_metadatas
        )

    async def index_all(self, vault_path):
        research_dir = os.path.join(vault_path, "KnowledgePipeline", "Research")

        if not os.path.exists(research_dir):
            return

        print(f"📂 Scanning vault: {research_dir}")
        for file_name in os.listdir(research_dir):
            if file_name.endswith(".md"):
                file_path = os.path.join(research_dir, file_name)
                await self.index_file(file_path)

    def read_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def extract_frontmatter(self, text: str):
        pattern = r"^---\s*\n(.*?)\n---\s*\n?"
        match = re.match(pattern, text, flags=re.DOTALL)

        if match:
            frontmatter_raw = match.group(1)
            metadata = yaml.safe_load(frontmatter_raw)
            content = text[match.end() :]
            return metadata, content

        return {}, text

    async def get_embeddings(self, chunks):
        semaphore = asyncio.Semaphore(10)

        if self.embedding_model == "nomic-embed-text":
            semaphore = asyncio.Semaphore(10)

            async def embedNomic(c):
                async with semaphore:
                    res = await asyncio.to_thread(
                        requests.post,
                        "http://localhost:11434/api/embeddings",
                        json={"model": "nomic-embed-text", "prompt": c},
                    )

                    data = res.json()
                    emb = data["embedding"]

                    return emb[0] if isinstance(emb[0], list) else emb

            tasks = [embedNomic(c) for c in chunks]
            return await asyncio.gather(*tasks)

        else:
            semaphore = asyncio.Semaphore(10)

            async def embedGemma(c):
                async with semaphore:
                    res = await asyncio.to_thread(
                        requests.post,
                        "http://localhost:11434/api/embeddings",
                        json={"model": "EmbeddingGemma", "prompt": c},
                    )

                    data = res.json()
                    emb = data["embedding"]

                    return emb[0] if isinstance(emb[0], list) else emb

            tasks = [embedGemma(c) for c in chunks]
            return await asyncio.gather(*tasks)
