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
            user = data['event_from_user']
            chat = data['event_chat']

            if user.id == chat.id:
                chat_t = None
                user_t = f"\nUser: {user.first_name} | {user.username} | {user.id} "
            else:
                user_t = f"\nUser: {user.first_name} | {user.username} | {user.id} "
                chat_t = f"\nChat: {chat.title} | {chat.id}" 

            text = f"Uhandled event:{user_t}{chat_t}"
            logger.debug(text)
