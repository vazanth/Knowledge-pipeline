import json
from utils.constants import RAG_PROMPT


class RagEngine:

    def __init__(self, vector_store, embedding_engine, gemini_llm_client):
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine
        self.gemini_llm_client = gemini_llm_client

    async def run_pipeline(self, query):
        embeddings = await self.embedding_engine.get_embeddings([query])

        # 1. Retrieve results (including distances)
        result = await self.vector_store.retrieve("EmbeddingGemma", embeddings, 5)

        context_parts = []
        sources_to_cite = set()
        best_distance = result["distances"][0][0] if result["distances"] else 2.0

        if best_distance < 1.3:
            for doc, meta in zip(result["documents"][0], result["metadatas"][0]):
                source_url = meta.get("source", "Unknown")
                source_title = meta.get("title", "Unknown Note")
                sources_to_cite.add(source_url)
                context_parts.append(f"--- SOURCE: [[{source_title}]] ---\n{doc}")
        else:
            # Tell Gemini explicitly that the vault is empty for this topic
            context_parts = ["NO RELEVANT CONTENT IN VAULT."]

        context = "\n\n".join(context_parts)
        prompt = RAG_PROMPT.format(context=context, query=query)
        response = await self.gemini_llm_client.generate(prompt)

        if sources_to_cite and "NO RELEVANT CONTENT" not in context:
            citation_text = "\n\n📚 **Sources from your vault:**\n"
            citation_text += "\n".join(
                [f"• {url}" for url in sources_to_cite if url.startswith("http")]
            )
            response += citation_text

        return response
