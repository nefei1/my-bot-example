import os
import sys
import asyncio
from contextlib import suppress
from loguru import Logger, logger
from aiohttp import web

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode 
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from src.handlers import get_routers
from src.middlewares import DbMiddleware, Throttling, UserMiddleware, CallbackMiddleware
from src.data import settings
from src.db import Base, UserManager
from src.keyboards import set_commands
from src.middlewares.unhandled import UnhandledMiddleware
from src.settings import Settings
from src.utils.func import custon_log, filter_level, format_filter

async def init_db(dp: Dispatcher):
    engine = create_async_engine(settings.DB_LINK)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        query = text("SELECT VERSION() as ver")
        res = await conn.execute(query)
        version = res.scalars().one()

    sessionmaker = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    dp['sessionmaker'] = sessionmaker

    dp.update.outer_middleware(DbMiddleware(sessionmaker=sessionmaker))

    logger.info(f"Succesfully connected to database\nVersion - {version}")

def init_loggers(dp: Dispatcher):
    logger.debug = custon_log(logger.debug)
    logger.error = custon_log(logger.error)
    logger.info = custon_log(logger.info)
    
    info_path = 'logs/info.log'
    debug_path = 'logs/debug.log'
    error_path = 'logs/error.log'
    unhandled_path = 'logs/unhandled.log'

    logger.level("UNHANDLED", no=38)

    logger.remove()

    logger.add(sys.stderr, format=format_filter)
    logger.add(info_path, filter=lambda record: filter_level(record, level='INFO'), format=format_filter, rotation="100MB")
    logger.add(debug_path, filter=lambda record: filter_level(record, level='DEBUG'), format=format_filter, rotation="100MB")
    logger.add(error_path, filter=lambda record: filter_level(record, level='ERROR'), format=format_filter,  rotation="100MB")
    logger.add(unhandled_path, filter=lambda record: filter_level(record, level='UNHANDLED'), format=format_filter,  rotation="100MB")

    logger.unhandled = lambda *a, **kw: logger.log("UNHANDLED", *a, *kw)
    logger.unhandled = custon_log(logger.unhandled)
    
def init_middlewares(dp: Dispatcher):
    dp.update.outer_middleware(UnhandledMiddleware())
    dp.message.middleware(Throttling())
    dp.callback_query.middleware(Throttling())
    dp.callback_query.middleware(CallbackMiddleware())
    dp.update.outer_middleware(UserMiddleware())

async def main():
    settings = Settings()

    bot = Bot(settings.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    storage = RedisStorage(redis=settings.redis_dsn()) if settings.redis_dsn() else None

    dp = Dispatcher(
        storage=storage,
        settings=settings
    )

    locales_path = os.path.join(os.path.abspath(__name__).replace(__name__, ''), "locales/{locale}/LC_MESSAGES")
    i18n_middleware = I18nMiddleware(core=FluentRuntimeCore(path=locales_path), manager=UserManager())

    init_loggers(dp)
    await init_db(dp)
    init_middlewares(dp)

    i18n_middleware.setup(dispatcher=dp)

    dp.workflow_data
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    handler_routers = get_routers()
    dp.include_routers(handler_routers)

    await set_commands(bot)

    if settings.webhooks:
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=settings.webhook_secret_token.get_secret_value()
        ).register(app, '/webhook')
        setup_application(app, dp, bot=bot)

        await web._run_app(app, host='0.0.0.0', port=8080)
    else:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

async def startup(bot: Bot, settings: Settings, dispatcher: Dispatcher):
    await bot.delete_webhook(drop_pending_updates=True)

    if settings.WEBHOOKS:
        logger.info("Bot succesfully started")
        await bot.set_webhook(
            url=settings.webhook_url.get_secret_value(),
            allowed_updates=dispatcher.resolve_used_update_types(),
            secret_token=settings.webhook_secret_token.get_secret_value()
            )
    else:
        logger.info("Bot succesfully started")

async def shutdown(bot: Bot):
    logger.info("Bot stopped")
    await bot.session.close()

if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())