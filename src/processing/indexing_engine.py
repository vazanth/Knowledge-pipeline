import re
from processing.chunk import get_chunks


class IndexingEngine:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    async def index_file(self, file_path):
        text = self.read_file(file_path)
        text = self.remove_frontmatter(text)

        chunks = get_chunks(text)
        embeddings = self.get_embeddings()

        # store_in_chroma(chunks, embeddings, file_path)

    def read_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def remove_frontmatter(self, text: str):
        pattern = r"^---\s*\n.*?\n---\s*\n"
        re.sub(pattern, "", text, flags=re.DOTALL)

    def get_embeddings(self):
        """"""
