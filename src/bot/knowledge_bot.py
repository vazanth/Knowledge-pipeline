import sys, logging
from core.container import AppContainer
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)
from bot.handlers import BotHandlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

for logger_name in ["httpx", "httpcore", "telegram", "apscheduler"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class KnowledgeBot:
    def __init__(self, container: AppContainer):
        self.token = container.token
        self.db = container.db
        self.handlers = BotHandlers(
            db=container.db,
            summarizer=container.summarizer,
            researcher=container.researcher,
            obsidian=container.obsidian,
            rag_engine=container.rag_engine,
        )

    # ─── Lifecycle Hooks ──────────────────────────────────────────

    async def post_init(self, application):
        """This runs INSIDE the bot's engine room."""
        await self.db.initialize_database()
        print("✅ Database initialized inside the Bot loop.")

    async def post_shutdown(self, application):
        await self.db.close()
        logger.info("🔒 Database connection closed cleanly.")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logging.error("Exception while handling an update:", exc_info=context.error)

        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "😅 Oops, something broke on my end.\nGive it another try in a bit!"
                )
        except Exception as e:
            print(f"error: {e}")
            sys.exit(1)

    # ─── App Wiring ───────────────────────────────────────────────

    def run(self):
        """This is the method you call from main.py"""
        app = (
            ApplicationBuilder()
            .token(self.token)
            .post_init(self.post_init)
            .post_shutdown(self.post_shutdown)
            .build()
        )

        # Command handlers
        app.add_handler(CommandHandler("start", self.handlers.start))
        app.add_handler(CommandHandler("add_source", self.handlers.add_source))
        app.add_handler(CommandHandler("latest", self.handlers.latest))
        app.add_handler(CommandHandler("sources", self.handlers.sources))
        app.add_handler(CommandHandler("query", self.handlers.query))

        # Callback & error handlers
        app.add_handler(CallbackQueryHandler(self.handlers.handle_callback))
        app.add_error_handler(self.error_handler)  # type: ignore

        print("🚀 Bot is polling...")
        app.run_polling()
