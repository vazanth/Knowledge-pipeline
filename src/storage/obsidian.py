from datetime import datetime
import os
import re


class ObsidianManager:

    def __init__(self, indexing_engine, vault_path: str) -> None:
        self.indexing_engine = indexing_engine
        self.vault_path = vault_path
        self.directory = os.path.join(self.vault_path, "KnowledgePipeline", "Research")
        os.makedirs(self.directory, exist_ok=True)

    def _sanitize_filename(self, filename: str):
        return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

    async def save_research(self, title: str, content: str, source_url: str):
        date_str = datetime.now().strftime("%Y-%m-%d")
        clean_title = self._sanitize_filename(title)
        filename = f"{clean_title}.md"
        file_path = os.path.join(self.directory, filename)

        frontmatter = (
            f"---\n"
            f'title: "{title}"\n'
            f"source: {source_url}\n"
            f"created: {date_str}\n"
            f"tags: [research, knowledge-pipeline]\n"
            f"---\n\n"
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(frontmatter + content)

        await self.indexing_engine.index_file(file_path)

        return file_path
