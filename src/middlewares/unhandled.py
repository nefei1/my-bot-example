from typing import Any, Awaitable, Callable, Dict
from loguru import logger

from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.types import TelegramObject
from aiogram import BaseMiddleware

class UnhandledMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ):
        res = await handler(event, data)
        if res is UNHANDLED:
            user = event.from_user
            chat = event.chat

            if not chat:
                chat_t = ''
                user_t = f"\n\n👤 User:\n   ├ 🆔 ID: {user.uid}\n   ├ 📛 Name: {user.first_name}\n   └ 📝 Username: {user.username or '\u2014'}"
            else:
                user_t = f"\n\n👤 User:\n   ├ 🆔 ID: {user.uid}\n   ├ 📛 Name: {user.first_name}\n   └ 📝 Username: {user.username or '\u2014'}"
                chat_t = f"\n\n💬 Chat:\n   ├ 🆔 ID: {chat.chat_id}\n   ├ 🏷️ Title: {chat.title}\n   └ 💡 Type: Group" 

            if event.message:
                event_t = f'\n\n🔧 Event: {event.message.text}'
            elif event.callback_query:
                event_t = f'\n\n🔧 Event: {event.callback_query.data}'
            else:
                event_t = ''

            text = f"Uhandled event:{user_t}{chat_t}{event_t}"
            logger.unhandled(text)