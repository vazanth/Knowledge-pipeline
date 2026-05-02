from dataclasses import dataclass


@dataclass
class Settings:
    telegram_token: str
    tavily_token: str
    vault_path: str
    sqlite_db_path: str
    chroma_db_path: str
