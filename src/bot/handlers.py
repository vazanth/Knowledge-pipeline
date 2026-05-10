from asyncio.exceptions import CancelledError
from pathlib import Path
import asyncio, logging
from datetime import datetime, timezone, timedelta

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
    Update,
)
from telegram.ext import ContextTypes

from adapters.sources.youtube import YoutubeAdapter
from bot.ui_helpers import get_message, get_callback_query, create_rolling_loader
from utils.constants import (
    ADD_SOURCE_ERROR,
    ADD_SOURCE_SUCCESS,
    ALL_CAUGHT_UP,
    GENERIC_ERROR,
    SOURCES_EMPTY,
    SOURCES_LIST,
    UPDATE_FOUND,
    UPDATES_CHECKING,
    UPDATES_EMPTY,
    UPDATES_LOADING,
    WELCOME_MESSAGE,
)

logger = logging.getLogger(__name__)


class BotHandlers:
    def __init__(self, db, summarizer, researcher, obsidian):
        self.db = db
        self.summarizer = summarizer
        self.researcher = researcher
        self.obsidian = obsidian
        self._research_cache = {}

    # ─── Command Handlers ─────────────────────────────────────────

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for the start command"""
        msg = get_message(update)
        await msg.reply_text(WELCOME_MESSAGE)

    async def add_source(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /add_source <platform_id> <name>"""
        if not context.args or len(context.args) < 2:
            msg = get_message(update)
            await msg.reply_text(ADD_SOURCE_ERROR)
            return

        platform_id = context.args[0]
        name = " ".join(context.args[1:])

        await self.db.create_source(name, "youtube", platform_id)

        msg = get_message(update)

        await msg.reply_text(
            ADD_SOURCE_SUCCESS.format(name=name),
            parse_mode="Markdown",
        )

    async def sources(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = get_message(update)
        await msg.reply_text(UPDATES_CHECKING)

        source_names = await self.db.fetch_source_names()

        if not source_names:
            await msg.reply_text(SOURCES_EMPTY)
            return

        names_str = "\n".join([f"• {name}" for name in source_names])

        await msg.reply_text(
            SOURCES_LIST.format(names_str=names_str), parse_mode="Markdown"
        )

    async def latest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = get_message(update)
        status_msg = await msg.reply_text(UPDATES_LOADING)

        sources = await self.db.fetch_all_sources()

        all_items = []
        for s in sources:
            last_check = await self.db.fetch_last_content_fetch_time(s["id"])
            last_max_check = datetime.now(timezone.utc) - timedelta(days=7)
            since = max(last_check, last_max_check)

            adapter = YoutubeAdapter(local_id=s["id"], platform_id=s["platform_id"])

            recent_items = await adapter.fetch_latest(since)

            if recent_items:
                all_items.extend([(item, s["name"]) for item in recent_items])

        if not all_items:
            await status_msg.edit_text(UPDATES_EMPTY)
            return

        await status_msg.edit_text(UPDATE_FOUND.format(count=len(all_items)))

        for idx, (item, source_name) in enumerate(all_items, start=1):

            async def progress_updater():
                steps = [
                    f"🔎 Processing {idx}/{len(all_items)}...",
                    "🧠 Understanding content...",
                    "✍️ Writing summary...",
                    "⚡ Almost done...",
                ]
                i = 0
                while True:
                    await asyncio.sleep(5)
                    try:
                        await status_msg.edit_text(steps[i % len(steps)])
                        i += 1
                    except CancelledError:
                        raise
                    except Exception:
                        pass

            task = asyncio.create_task(progress_updater())
            try:
                summary, strategy = await self.summarizer.run_pipeline(
                    item.content, "transcript"
                )

                content_id = await self.db.create_content(
                    source_id=item.source_id,
                    platform_content_id=item.platform_content_id,
                    title=item.title,
                    content=item.content,
                    content_url=item.content_url,
                    content_hash=item.content_hash,
                )

                keyboard = [
                    InlineKeyboardButton(
                        "📚 Explore More",
                        callback_data=f"research:{content_id}",
                    )
                ]

                await self.db.create_summary(content_id, summary, strategy)
                thumbnail_url = f"https://img.youtube.com/vi/{item.platform_content_id}/maxresdefault.jpg"
                caption = (
                    f"📺 *{item.title}*\n📡 _{source_name}_\n..."
                    f"🔗 [Watch here]({item.content_url})\n\n"
                    f"📝 *Summary:*\n{summary}\n\n"
                )

                await msg.reply_photo(
                    photo=thumbnail_url,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([keyboard]),
                )

            finally:
                task.cancel()
                try:
                    await task
                except CancelledError:
                    pass

        await status_msg.edit_text(ALL_CAUGHT_UP)

    # ─── Callback Handlers ────────────────────────────────────────

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query: CallbackQuery = get_callback_query(update)
        await query.answer()

        if not query.message or not isinstance(query.message, Message):
            return

        caption: str = ""
        if isinstance(query.message, Message):
            caption = query.message.caption or ""

        async def ui_update(text):
            await query.edit_message_caption(
                caption=caption + "\n\n" + text, parse_mode="Markdown"
            )

        if not query.data:
            return
        callback_payload = query.data.split(":")
        action = callback_payload[0]

        if action == "research":
            try:
                await self.run_research_pipeline(query, callback_payload)
            except Exception as e:
                logging.error(f"Research pipeline failed: {e}")
                await ui_update(f"❌ *Research failed:* {str(e)}")

        if action == "view":
            await self.render_summary_view(query, callback_payload)

        if action == "download":
            file_path = await self.save_and_send_summary(callback_payload, query)

            if not file_path:
                await query.message.edit_text(GENERIC_ERROR)
                return
            path = Path(file_path)

            with path.open("rb") as f:
                await query.message.reply_document(
                    document=f,
                    filename=path.name,
                    caption="📚 Here's your research report!",
                )

    # ─── Pipeline Logic ───────────────────────────────────────────

    async def run_research_pipeline(self, query, callback_payload):
        content_id = int(callback_payload[1])

        await query.edit_message_reply_markup(reply_markup=None)

        research_msg = await query.message.reply_text(
            "🔬 *Initializing Research...*", parse_mode="Markdown"
        )

        async def ui_update(text, reply_markup=None):
            try:
                await research_msg.edit_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
            except CancelledError:
                raise
            except Exception:
                pass

        await ui_update(f"📊 Insights for content `{content_id}`\n\nComing soon...")

        summary_text = await self.db.fetch_content_summaries(content_id)

        if not summary_text:
            return

        steps = [
            "🧠 Thinking really hard...",
            "🔍 Asking the internet nicely...",
            "🌐 Sneaking into webpages...",
            "🧩 Cutting info into snackable bits...",
            "🤯 Having a mini genius moment...",
            "✍️ Typing something brilliant...",
            "🎉 Wrapping it up for you...",
        ]
        loader = await create_rolling_loader(ui_update, steps)

        scraped_data, source_urls = await self.researcher.run_pipeline(
            summary_text, ui_update
        )

        # Filter out failed scrapes (None values) and pass only the text content
        articles = [text for text in scraped_data.values() if text]

        if len(articles) < 3:
            raise RuntimeError(
                f"Only {len(articles)} valid articles scraped. "
                "Try different search queries or increase max_results in Tavily."
            )

        citations = "\n## Sources: \n" + "\n".join([f"- {url}" for url in source_urls])
        try:
            report = await self.summarizer.run_pipeline_list(articles)
        finally:
            loader.cancel()

        self._research_cache[content_id] = {
            "full": report + citations,
            "top_urls": source_urls[:5],
        }

        keyboard = [
            [
                InlineKeyboardButton("👁 View", callback_data=f"view:{content_id}"),
                InlineKeyboardButton(
                    "⬇️ Download",
                    callback_data=f"download:{content_id}",
                ),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await ui_update(
            "✅ *Research complete!*\nWhat would you like to do?",
            reply_markup=reply_markup,
        )

    async def render_summary_view(self, query, callback_payload):
        content_id = int(callback_payload[1])
        data = self._research_cache.get(content_id)
        if not data:
            await query.message.reply_text("Content expired. Please regenerate.")
            return

        report = data["full"]
        citations = data["top_urls"]

        # Telegram message limit is 4096 chars — truncate if needed
        if len(report) > 4000:
            report = (
                report[:1000] + "\n\n... _(truncated, use Download for full report)_"
            )

        ui_citations = "\n\n🌐 **Top Sources:**\n" + "\n".join(
            [f"• {url}" for url in citations]
        )
        keyboard = [
            [InlineKeyboardButton("⬇️ Download", callback_data=f"download:{content_id}")]
        ]

        await query.message.reply_text(
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True,
            text=report + ui_citations,
        )

    async def save_and_send_summary(self, callback_payload, query):
        content_id = int(callback_payload[1])
        data = self._research_cache.get(content_id)

        async def ui_update(text):
            try:
                await query.message.edit_text(text, parse_mode="Markdown")
            except:
                pass

        if not data:
            await ui_update("Content expired. Please regenerate.")
            return None

        report = data["full"]

        row = await self.db.fetch_content_by_id(content_id)
        title = row["title"] if row else "Research"
        source_url = row["content_url"] if row else ""

        await ui_update("📂 Saving research to Obsidian...")
        file_path = await self.obsidian.save_research(
            title=title, content=report, source_url=source_url
        )

        await ui_update(f"📑 Research saved to your vault!\n📍 {file_path}")

        return file_path
