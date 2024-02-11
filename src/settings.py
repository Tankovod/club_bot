from aiogram import Bot

from src.types.settings import settings

bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
