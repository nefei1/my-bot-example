from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from loguru import logger


class UserMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ):
        db = data['db']
        event_user = data['event_from_user']

        uid = event_user.id

        user = await db.get_user(uid)
        if not user:
            language = event_user.language_code if event_user.language_code in ["en", "ru"] else 'en'
            user = await db.create_user(event_user, language=language)
            logger.info(f"User with id {uid} was added")

        else:
            user.first_name = event_user.first_name

        data['user'] = user
        
        return await handler(event, data)
        