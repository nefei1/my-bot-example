from typing import Any, Callable, Dict, Awaitable, Union
from cachetools import TTLCache

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from aiogram.dispatcher.flags import get_flag

class Throttling(BaseMiddleware):

    def __init__(self, throttle_time: float = 1.5):
        self.caches = {
            "default": TTLCache(maxsize=10_000, ttl=throttle_time),
            "callback": TTLCache(maxsize=10_000, ttl=throttle_time)
        }

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], 
        event: Union[CallbackQuery, Message],
        data: Dict[str, Any]
    ) -> Awaitable:
        if isinstance(event, Message):
            uid = event.from_user.id
            
        if isinstance(event, CallbackQuery):
            uid = event.message.from_user.id

        throttling_key = get_flag(data, 'throttiling_key', default='default')

        if throttling_key is not None and throttling_key in self.caches:
            if isinstance(event, Message):
                if event.from_user.id in self.caches[throttling_key]:
                    return
                else:
                    self.caches[throttling_key][event.from_user.id] = None
            else:
                throttling_key = "callback"
                if event.message.from_user.id in self.caches[throttling_key]:
                    await event.answer()
                    return
                else:
                    self.caches[throttling_key][event.message.from_user.id] = None

        return await handler(event, data)