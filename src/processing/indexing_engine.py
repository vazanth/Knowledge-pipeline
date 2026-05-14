import os
from pathlib import Path
import yaml
import re
from processing.chunk import get_chunks


class IndexingEngine:

    def __init__(self, vector_store, embedding_engine):
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine

    async def index_file(self, file_path):
        text = self.read_file(file_path)
        metadata, text = self.extract_frontmatter(text)

        clean_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                clean_metadata[key] = value
            elif isinstance(value, list):
                clean_metadata[key] = ", ".join(map(str, value))
            else:
                clean_metadata[key] = str(value)

        if "source" not in clean_metadata:
            clean_metadata["source"] = Path(file_path).name

        chunks = get_chunks(text, "markdown")

        ids = [f"{Path(file_path).name}_{i}" for i in range(len(chunks))]

        chunk_metadatas = [clean_metadata for _ in chunks]

        embeddings = await self.embedding_engine.get_embeddings(chunks)

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
