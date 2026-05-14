import asyncio
import requests


class EmbeddingEngine:

    def __init__(self, embedding_model="default") -> None:
        self.embedding_model = embedding_model

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
