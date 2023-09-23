import os
from dotenv import load_dotenv

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode

load_dotenv("config.env")

bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
