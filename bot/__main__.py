import logging
from asyncio import run

from aiogram import Dispatcher
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from src.handlers.handlers import router
from src.settings import bot

logging.basicConfig(level=logging.INFO)


async def on_startup():
    await bot.set_my_commands(
        commands=[
            BotCommand(command='/events', description='🤠 Проекты'),
            BotCommand(command='/edit', description='🕺  Настройка Уведомлений'),
            BotCommand(command='/start', description='💫 Рестарт бота'),
            BotCommand(command='/about', description='👒 О боте')
        ],
        scope=BotCommandScopeAllPrivateChats(),
        language_code='ru'
    )
    await bot.set_my_commands(
        commands=[
            BotCommand(command='/events', description='🤠 Проекты'),
            BotCommand(command='/edit', description='🕺  Настройка Уведомлений'),
            BotCommand(command='/start', description='💫 Рестарт бота'),
            BotCommand(command='/about', description='👒 О боте')
        ],
        scope=BotCommandScopeAllPrivateChats(),
        language_code='by'
    )
    await bot.set_my_commands(
        commands=[
            BotCommand(command='/events', description='🤠 Projects'),
            BotCommand(command='/edit', description='🕺 Notification Config'),
            BotCommand(command='/start', description='💫 Bot Restart'),
            BotCommand(command='/about', description='👒 About')
        ],
        scope=BotCommandScopeAllPrivateChats(),
        language_code='en'
    )

dp = Dispatcher()


async def main():
    dp.include_router(router=router)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == '__main__':
    run(main())
