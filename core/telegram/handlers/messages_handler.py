from .. import buttons
from .. import functions as func
from ..bot_instance import bot
from aiogram import types, F, Router

from core.backend.models import db, Folder, Note
from core.backend import constants as C

router = Router()


@router.message()
async def messages_handler(message: types.Message):
    user_id = message.chat.id
    status = await db.get_status(user_id=user_id)
    print("status:", status)
    if status == C.status_empty or status == None:
        new_mes = await message.answer(text="<b>Главное меню</b>", reply_markup=buttons.menu)
        message_id_to_del = await db.get_buttons_message_id(user_id=user_id)
        await bot.delete_message(chat_id=user_id, message_id=message_id_to_del)
        await db.set_buttons_message_id(user_id=user_id, new_message_id=new_mes.message_id)
        return

    text = message.html_text
    message_id_to_edit = await db.get_buttons_message_id(user_id=user_id)

    if status.startswith(C.status_updating_note):
        note_id = status.removeprefix(C.status_updating_note)
        note = await Note(id=note_id).connect()

        to_instruct = False
        if note.message_id == None:  # В дальнейшем расширить, чтобы можно было изменять это сообщение
            print("note.message_id == None")
            await note.update_message_id(new_message_id=message.message_id)
            await note.update_content(new_content=text)

            to_instruct = True

        else:
            adding_rule = await db.get_rule_adding(user_id=user_id)

            if adding_rule == True:
                new_content = note.content + "\n\n" + text
                await note.update_content(new_content=new_content)

        await func.display_note(
            user_id=user_id,
            message_id=message_id_to_edit,
            note=note,
            new_message_id_to_reply=await db.get_note_message_id(note_id=note_id),
        )
        await db.set_status(user_id=user_id, new_status=C.status_empty)

        if to_instruct:
            mes_id_to_del = await db.get_buttons_message_id(user_id=user_id) + 1
            await message.answer(
                text="Чтобы отредактировать заметку, перейдите к прикреплённому сообщению и измените его.\nТекст заметки автоматически изменится",
                reply_markup=buttons.ok,
            )
            await func.delete_message_after_minutes(minutes=3, chat_id=user_id, message_id=mes_id_to_del)

    if status.startswith(C.status_updating_folder_name):
        folder_id = status.removeprefix(C.status_updating_folder_name)
        await Folder(id=folder_id).update(new_name=text)
        await func.upd_folders_keyboard(user_id=user_id, message_id=message_id_to_edit)
        await db.set_status(user_id=user_id, new_status=C.status_empty)
        await bot.delete_message(chat_id=user_id, message_id=message.message_id)

    elif status.startswith(C.status_updating_note_title):
        note_id = status.removeprefix(C.status_updating_note_title)
        note = await Note(id=note_id).connect()
        print("note.id, note_id", note.id, note_id)
        print("old note.title", note.title)
        await note.update_title(new_title=text)
        print("new note.title", note.title)
        await func.display_notes_keyboard(
            user_id=user_id, message_id=message_id_to_edit, folder_id=note.folder_id
        )
        await db.set_status(user_id=user_id, new_status=C.status_empty)
        await bot.delete_message(chat_id=user_id, message_id=message.message_id)

    elif status.startswith(C.status_updating_note_message_id):
        note_id = status.removeprefix(C.status_updating_note_message_id)
        await db.set_note_message_id(user_id=user_id, new_message_id=message.message_id)
        note = await Note(id=note_id).connect()

        await func.display_note(
            user_id=user_id,
            message_id=message_id_to_edit,
            note=note,
            new_message_id_to_reply=message.message_id,
        )
        await db.set_status(user_id=user_id, new_status=C.status_empty)


@router.edited_message(F.from_user.id != bot.id)
async def edit_messages_handler(message: types.Message):
    user_id = message.chat.id
    # status = await db.get_status(user_id=user_id)

    text = message.html_text
    note_messages_ids = await db.get_notes_messages_ids(user_id=user_id)

    if message.message_id in note_messages_ids:
        note = await Note(message_id=message.message_id, user_id=user_id).connect()
        await note.update_content(new_content=text)
        message_id_to_edit = await db.get_buttons_message_id(user_id=user_id)
        await func.display_note(user_id=user_id, message_id=message_id_to_edit, note_id=note.id)
