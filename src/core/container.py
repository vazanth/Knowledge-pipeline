from dataclasses import dataclass
from typing import Any

from processing import indexing_engine


@dataclass
class AppContainer:
    token: str
    default_llm_client: Any
    gemini_llm_client: Any
    summarizer: Any
    researcher: Any
    db: Any
    obsidian: Any
    indexing_engine: Any
