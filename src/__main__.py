import os
import sys
import asyncio
from loguru import logger
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

async def init_db(dp: Dispatcher):
    engine = create_async_engine(config.DB_LINK)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        query = text("SELECT VERSION() as ver")
        res = await conn.execute(query)
        version = res.scalars().one()

    db_logger = dp['db_logger']

    sessionmaker = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    dp['sessionmaker'] = sessionmaker

    dp.update.outer_middleware(DbMiddleware(sessionmaker=sessionmaker))

    db_logger.info(f"Succesfully connected to database\nVersion - {version}")

def make_filter(name):
    def filter(record):
        return record["extra"].get("name") == name
    return filter

def init_loggers(dp: Dispatcher):
    folder_dir = os.path.join(os.path.dirname(os.path.abspath(__name__)).replace("\\src", ''), 'logs')
    aiogram_file_dir = os.path.join(folder_dir, "aiogram_logs.txt")
    database_file_dir = os.path.join(folder_dir, "database_logs.txt")

    fmt = "[{level}]\n| Time: <green>{time:YYYY-MM-DD HH:mm:ss}</green>\n| File-func-line: <cyan>{name}:{function}:</cyan><red>{line}</red>\n<yellow>{message}</yellow>\n"

    logger.remove()
    logger.add(sys.stderr, format=fmt)
    logger.add(aiogram_file_dir, format=fmt, filter=make_filter('aiogram'), rotation="100MB")
    logger.add(database_file_dir, format=fmt, filter=make_filter("database"), rotation="100MB")

    aiogram_logger = logger.bind(name="aiogram")
    database_logger = logger.bind(name="database")

    dp["aio_logger"] = aiogram_logger
    dp["db_logger"] = database_logger
    
def init_middlewares(dp: Dispatcher):
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

async def startup(bot: Bot, aio_logger):
    if config.WEBHOOK_URL:
        aio_logger.info("Bot succesfully started")
        await bot.set_webhook(f"{config.WEBHOOK_URL}{config.WEBHOOK_SERVER_PATH}")
    else:
        aio_logger.info("Bot succesfully started")

async def shutdown(bot: Bot, aio_logger):
    aio_logger.info("Bot stopped")
    await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass