from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class CallbackMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ):
        call_uid = int(event.data.split(':')[-1])
        event_uid = event.from_user.id
        if call_uid != event_uid:
            i18n = data['i18n']
            await event.answer(i18n.get("call_incorrect_user"))
            return

        else:
            await handler(event, data)