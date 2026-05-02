from settings.load_settings import load_settings
from core.factory import AppFactory
from bot.knowledge_bot import KnowledgeBot


def start_app():
    try:
        config = load_settings()
    except ValueError as e:
        print(f"❌ Config error: {e}")
        return

    container = AppFactory.create(config)

    bot = KnowledgeBot(container)

    bot.run()


if __name__ == "__main__":
    start_app()
