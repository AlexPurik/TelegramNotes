from .. import buttons
from ..bot_instance import bot
from aiogram import types
from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command

from core.backend.models import db, Storage


router = Router()


@router.message(Command("start"))
async def start_command_handler(message: types.Message):
    user_id = message.chat.id
    message_id = message.message_id

    storage = Storage(user_id=user_id)
    await storage.connect()

    buttons_message_id = await db.get_buttons_message_id(user_id=user_id)
    if buttons_message_id:
        try:
            await bot.delete_message(chat_id=user_id, message_id=buttons_message_id)
        except TelegramBadRequest:
            pass

    await message.answer(text="<b>Главное меню</b>", reply_markup=buttons.menu)
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)

    await db.set_buttons_message_id(user_id=user_id, new_message_id=message_id + 1)


# @router.message(Command("help"))
# async def start_command_handler(message: types.Message):
#     user_id = message.chat.id
#     message_id = message.message_id
#     storage = Storage(user_id=user_id)
#     await message.answer(text="<b>Главное меню</b>", reply_markup=buttons.menu)
#

# @router.message(Command("info"))
# async def start_command_handler(message: types.Message):
#     user_id = message.chat.id
#     message_id = message.message_id
#     storage = Storage(user_id=user_id)
#     await message.answer(text="<b>Главное меню</b>", reply_markup=buttons.menu)
#

# @router.message(Command("settings"))
# async def start_command_handler(message: types.Message):
#     user_id = message.chat.id
#     message_id = message.message_id
#     storage = Storage(user_id=user_id)
#     await message.answer(text="<b>Главное меню</b>", reply_markup=buttons.menu)
#
