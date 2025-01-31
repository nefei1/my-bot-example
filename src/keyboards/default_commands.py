from aiogram import Bot
from aiogram.types import BotCommand

user_commands = {
    "en": {
        '/start': 'Start message',
        "/lang": "🇺🇸 Change language",
        },
    "ru": {
        "/start": "Начальное сообщение",
        '/lang': "🇷🇺 Сменить язык"
    }
    }

async def set_commands(bot: Bot):
    await bot.delete_my_commands()

    for lang in user_commands:

        await bot.set_my_commands(

            [BotCommand(command=command, description=description) for command, description in user_commands[lang].items()],

        )