import os
from dotenv import load_dotenv
from pathlib import Path

from adapters.extractors.jina_client import JinaExtractorClient
from adapters.llm import gemini_client
from adapters.llm.ollama_client import OllamaClient
from adapters.retrieval.tavily_client import TavilyRetrievalClient
from bot.telegram_bot import KnowledgeBot
from processing.researcher import Researcher
from processing.summarizer import Summarizer
from storage.database import DatabaseManager
from storage.obsidian import ObsidianManager


def start_app():
    env_path = Path(__file__).parent.parent / "config" / ".env"
    load_dotenv(env_path)
    telegram_token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    tavily_token = (os.getenv("TAVILY_API_KEY") or "").strip()
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")

    if not all([telegram_token, tavily_token]):
        print("❌ ERROR: tokens not found in .env file!")
        return
    if not vault_path:
        print("❌ ERROR: OBSIDIAN_VAULT_PATH not found!")
        return

    db_path = Path(__file__).parent.parent / "data" / "pipeline.db"

    db = DatabaseManager(str(db_path))

    default_llm_client = OllamaClient(model="gemma4:e2b")
    gemini_llm_client = gemini_client.GeminiClient(model="gemini-2.5-flash")

    tavily_client = TavilyRetrievalClient(api_key=tavily_token)

    jina_client = JinaExtractorClient()

    researcher = Researcher(
        llm_client=default_llm_client,
        tavily_client=tavily_client,
        jina_client=jina_client,
    )

    summarizer = Summarizer(
        default_llm_client=default_llm_client, gemini_llm_client=gemini_llm_client
    )

    obsidian = ObsidianManager(vault_path=vault_path)

    bot = KnowledgeBot(
        token=telegram_token,
        db=db,
        summarizer=summarizer,
        researcher=researcher,
        llm_client=default_llm_client,
        obsidian=obsidian,
        adapter=None,
    )

    bot.run()


if __name__ == "__main__":
    start_app()
