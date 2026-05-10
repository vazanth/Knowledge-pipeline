import asyncio
from asyncio.exceptions import CancelledError
from typing import cast
from telegram import CallbackQuery, Message


def get_message(update) -> Message:
    return cast(Message, update.message)


def get_callback_query(update) -> CallbackQuery:
    return cast(CallbackQuery, update.callback_query)


async def create_rolling_loader(ui_update, steps, interval=20):
    async def _roller():
        i = 0
        while True:
            await asyncio.sleep(interval)
            try:
                await ui_update(steps[i % len(steps)])
                i += 1
            except CancelledError:
                raise
            except Exception:
                pass

    return asyncio.create_task(_roller())
