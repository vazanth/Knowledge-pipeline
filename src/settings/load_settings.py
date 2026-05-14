import os
from pathlib import Path
from settings.settings import Settings
from dotenv import load_dotenv


def load_settings() -> Settings:
    root_path = Path(__file__).parent.parent.parent

    env_path = root_path / ".env"

    print(f"rootpath {root_path}")
    print(f"env_path {env_path.resolve()}")

    load_dotenv(env_path)

    telegram_token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    tavily_token = (os.getenv("TAVILY_API_KEY") or "").strip()
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")

    sqlite_db_path: Path = root_path / "data" / "pipeline.db"

    chroma_db_path: Path = root_path / "data"

    if not telegram_token:
        print("❌ ERROR: telegram token not found in .env file!")
        raise ValueError("TELEGRAM_BOT_TOKEN not found in .env")

    if not tavily_token:
        print("❌ ERROR: tavily token not found in .env file!")
        raise ValueError("TAVILY_API_KEY not found in .env")

    if not vault_path:
        print("❌ ERROR: OBSIDIAN_VAULT_PATH not found!")
        raise ValueError("OBSIDIAN_VAULT_PATH not found in .env")

    return Settings(
        telegram_token=telegram_token,
        tavily_token=tavily_token,
        vault_path=vault_path,
        sqlite_db_path=str(sqlite_db_path),
        chroma_db_path=str(chroma_db_path),
    )
