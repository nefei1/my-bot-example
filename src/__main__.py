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
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from src.handlers import get_routers
from src.middlewares import DbMiddleware, Throttling, UserMiddleware, CallbackMiddleware
from src.data import config
from src.db import Base, UserManager
from src.keyboards import set_commands
from src.middlewares.unhandled import UnhandledMiddleware

async def init_db(dp: Dispatcher):
    engine = create_async_engine(config.DB_LINK)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        query = text("SELECT VERSION() as ver")
        res = await conn.execute(query)
        version = res.scalars().one()

    sessionmaker = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    dp['sessionmaker'] = sessionmaker

    dp.update.outer_middleware(DbMiddleware(sessionmaker=sessionmaker))

    logger.info(f"Succesfully connected to database\nVersion - {version}")

def format_filter(message):
    if message["level"].name == "ERROR":
        return "\n[<red>{level}</red>]\n\n| Time: <b><green>{time:YYYY-MM-DD HH:mm:ss}</green></b>\n| File-func-line: <cyan>{name}:{function}:</cyan><red>{line}</red>\n<b><red>{message}</red></b>\n"
    elif message["level"].name in ["WARNING", "DEBUG"]:
        return "\n[<yellow>{level}</yellow>]\n\n| Time: <b><green>{time:YYYY-MM-DD HH:mm:ss}</green></b>\n| File-func-line: <cyan>{name}:{function}:</cyan><red>{line}</red>\n<b><yellow>{message}</yellow></b>\n"
    else:
        return "\n[<green>{level}</green>]\n\n| Time: <b><green>{time:YYYY-MM-DD HH:mm:ss}</green></b>\n| File-func-line: <cyan>{name}:{function}:</cyan><red>{line}</red>\n<b><green>{message}</green></b>\n"

def filter_level(record, level):
    return record["level"].name == level

def init_loggers(dp: Dispatcher):
    info_path = 'logs/info.log'
    debug_path = 'logs/debug.log'
    error_path = 'logs/error.log'

    logger.remove()
    logger.add(sys.stderr, format=format_filter)
    logger.add(info_path, filter=lambda record: filter_level(record, level='INFO'), format=format_filter, rotation="100MB")
    logger.add(debug_path, filter=lambda record: filter_level(record, level='DEBUG'), format=format_filter, rotation="100MB")
    logger.add(error_path, filter=lambda record: filter_level(record, level='ERROR'), format=format_filter,  rotation="100MB")
    
def init_middlewares(dp: Dispatcher):
    dp.update.outer_middleware(UnhandledMiddleware())
    dp.message.middleware(Throttling())
    dp.callback_query.middleware(Throttling())
    dp.callback_query.middleware(CallbackMiddleware())
    dp.update.outer_middleware(UserMiddleware())

async def main():
    bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    locales_path = os.path.join(os.path.abspath(__name__).replace(__name__, ''), "locales/{locale}/LC_MESSAGES")
    i18n_middleware = I18nMiddleware(core=FluentRuntimeCore(path=locales_path), manager=UserManager())

    init_loggers(dp)
    await init_db(dp)
    init_middlewares(dp)

    i18n_middleware.setup(dispatcher=dp)

    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    handler_routers = get_routers()
    dp.include_routers(handler_routers)

    await set_commands(bot)

    if config.WEBHOOK_URL:
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        webhook_requests_handler.register(app, path=config.WEBHOOK_SERVER_PATH)

        setup_application(app, dp, bot=bot)

        await bot.delete_webhook(drop_pending_updates=True)

        await web._run_app(app, host=config.WEBHOOK_SERVER_HOST)
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

async def startup(bot: Bot):
    if config.WEBHOOK_URL:
        logger.info("Bot succesfully started")
        await bot.set_webhook(f"{config.WEBHOOK_URL}{config.WEBHOOK_SERVER_PATH}")
    else:
        logger.info("Bot succesfully started")

async def shutdown(bot: Bot):
    logger.info("Bot stopped")
    await bot.session.close()

if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())