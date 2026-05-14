from processing.embedding_engine import EmbeddingEngine
from processing.rag_engine import RagEngine
from storage.vector_store import VectorStore
from adapters.extractors.jina_client import JinaExtractorClient
from adapters.llm.gemini_client import GeminiClient
from adapters.llm.ollama_client import OllamaClient
from adapters.retrieval.tavily_client import TavilyRetrievalClient
from processing.indexing_engine import IndexingEngine
from settings.settings import Settings
from core.container import AppContainer
from processing.researcher import Researcher
from processing.summarizer import Summarizer
from storage.database import DatabaseManager
from storage.obsidian import ObsidianManager


class AppFactory:
    @staticmethod
    def create(settings: Settings) -> AppContainer:

        db = DatabaseManager(str(settings.sqlite_db_path))

        default_llm_client = OllamaClient(model="gemma4:e2b")
        gemini_llm_client = GeminiClient(model="gemini-2.5-flash")

        tavily_client = TavilyRetrievalClient(api_key=settings.tavily_token)

        jina_client = JinaExtractorClient()

        researcher = Researcher(
            llm_client=default_llm_client,
            tavily_client=tavily_client,
            jina_client=jina_client,
        )

        summarizer = Summarizer(
            default_llm_client=default_llm_client, gemini_llm_client=gemini_llm_client
        )

        vector_store = VectorStore(chroma_db_path=settings.chroma_db_path)

        embedding_engine = EmbeddingEngine()

        indexing_engine = IndexingEngine(
            vector_store=vector_store, embedding_engine=embedding_engine
        )

        obsidian = ObsidianManager(
            indexing_engine=indexing_engine, vault_path=settings.vault_path
        )

        rag_engine = RagEngine(
            vector_store=vector_store,
            embedding_engine=embedding_engine,
            gemini_llm_client=gemini_llm_client,
        )

        return AppContainer(
            token=settings.telegram_token,
            default_llm_client=default_llm_client,
            gemini_llm_client=gemini_llm_client,
            summarizer=summarizer,
            researcher=researcher,
            db=db,
            obsidian=obsidian,
            indexing_engine=indexing_engine,
            embedding_engine=embedding_engine,
            rag_engine=rag_engine,
        )
