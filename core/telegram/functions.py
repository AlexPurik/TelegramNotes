from aiogram.exceptions import TelegramBadRequest
from . import buttons
from .bot_instance import bot

from core.backend.models import db, Storage, Folder, Note
from core.backend import constants as C
from core.schedule.schedule import scheduler
from core.schedule.triggers import OffsetTrigger


async def upd_folders_keyboard(user_id, message_id, storage=None, folders=None):
    if folders:
        folders = folders
    elif storage:
        folders = storage.folders
    else:
        storage = await Storage(user_id=user_id).connect()
        folders = storage.folders

    reply_markup = buttons.assemble_folder_kb(folders=folders)

    await bot.edit_message_text(
        text=f"<b>Папки</b> {C.storage_message_emoji}",
        chat_id=user_id,
        message_id=message_id,
        reply_markup=reply_markup,
    )


async def display_notes_keyboard(user_id, message_id, folder_id=None, folder=None, is_reply: bool = False):
    folder = folder or await Folder(id=folder_id).connect()

    reply_markup = buttons.assemble_notes_kb(folder.notes, folder.id)

    if is_reply == True:
        new_mes = await bot.send_message(
            text=f"{C.folder_message_emoji} <b>{folder.name}</b>",
            chat_id=user_id,
            reply_markup=reply_markup,
        )
        await bot.delete_message(chat_id=user_id, message_id=message_id)
        await db.set_buttons_message_id(user_id=user_id, new_message_id=new_mes.message_id)

    elif is_reply == False:
        await bot.edit_message_text(
            text=f"{C.folder_message_emoji} <b>{folder.name}</b>",
            chat_id=user_id,
            message_id=message_id,
            reply_markup=reply_markup,
        )


async def display_note(
    user_id, message_id, note_id=None, note=None, new_message_id_to_reply: int = None, first_time=False
):
    note = note or await Note(id=note_id).connect()
    note_id = note.id
    btn = await buttons.assemble_single_note_kb(folder_id=note.folder_id)

    text = f"ㅤ\n✏️ <b>{note.title}</b>\nㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ\n{note.content}"

    if new_message_id_to_reply:
        try:
            new_mes = await bot.send_message(
                text=text,
                chat_id=user_id,
                reply_markup=btn,
                reply_to_message_id=new_message_id_to_reply,
            )
            await bot.delete_message(chat_id=user_id, message_id=message_id)
            await db.set_buttons_message_id(user_id, new_mes.message_id)
        except TelegramBadRequest:
            try:
                await bot.edit_message_text(
                    text=text, chat_id=user_id, message_id=message_id, reply_markup=btn
                )
            except TelegramBadRequest:
                pass

    else:
        try:
            await bot.edit_message_text(text=text, chat_id=user_id, message_id=message_id, reply_markup=btn)
        except TelegramBadRequest:
            pass

    await db.set_status(user_id=user_id, new_status=f"{C.status_updating_note}{note_id}")


async def delete_message_after_minutes(chat_id, message_id, minutes: int = 5):
    print("job_added")
    scheduler.add_job(
        delete_message,
        id=f"{C.job_id_from_message}{message_id}",
        args=[chat_id, message_id],
        trigger=OffsetTrigger(minutes=minutes),
    )


async def revoke_message_id(user_id: int, content: str):
    note = Note(user_id=user_id, content=content)


async def delete_message(chat_id, message_id):
    print(f"deleting message {message_id}")
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
