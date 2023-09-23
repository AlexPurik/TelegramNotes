from aiogram import types, Router
from ..bot_instance import bot
from .. import buttons
from .. import functions as func

from core.backend.models import db, Storage, Folder, Note
from core.backend import constants as C
from core.schedule import schedule

router = Router()


@router.callback_query()
async def handle_callback_query(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    data = callback_query.data
    print(data)

    match data:
        case C.data_see_folders:
            storage = await Storage(user_id=user_id).connect()
            await func.upd_folders_keyboard(user_id=user_id, message_id=message_id, storage=storage)
            if not storage.folders:
                await callback_query.answer(
                    text="Чтобы создать новую папку, нажмите\n\n➕ Создать", show_alert=True
                )

        case C.data_to_main_menu:
            await bot.edit_message_text(
                text="<b>Главное меню</b>",
                chat_id=user_id,
                message_id=message_id,
                reply_markup=buttons.menu,
            )

        case C.data_new_folder:
            folder = Folder(user_id=user_id)
            await folder.connect()
            await callback_query.answer(text="Напишите имя папки", show_alert=True)
            await func.upd_folders_keyboard(user_id=user_id, message_id=message_id)
            await db.set_status(user_id=user_id, new_status=f"{C.status_updating_folder_name}{folder.id}")

        case C.data_edit_folders:
            btn = callback_query.message.reply_markup
            btn.inline_keyboard[0] = [
                {
                    "text": "❌ Отмена                                                                                                                ",
                    "callback_data": C.data_see_folders,
                }
            ]

            for kb in btn.inline_keyboard[1:]:
                for b in kb:
                    if b.callback_data.startswith(C.data_open_folder):
                        b.callback_data = (
                            f"{C.data_edit_folder}{b.callback_data.removeprefix(C.data_open_folder)}"
                        )
                        b.text = b.text.replace(C.folder_button_emoji, "✏️").replace("»", " ")

            await bot.edit_message_text(
                text=f"Выберите {C.folder_button_emoji} папку для редактирования",
                chat_id=user_id,
                message_id=message_id,
                reply_markup=btn,
            )

        case C.data_see_settings:
            await bot.edit_message_text(
                text="<b>Настройки</b>",
                chat_id=user_id,
                message_id=message_id,
                reply_markup=buttons.settings,
            )

        case C.data_edit_notes:
            btn = callback_query.message.reply_markup
            for kb in btn.inline_keyboard:
                for b in kb:
                    dat = b.callback_data
                    if dat.startswith(C.data_new_note):
                        folder_id = dat.removeprefix(C.data_new_note)
                        print("folder_id", folder_id)
                    elif dat.startswith(C.data_open_note):
                        b.callback_data = (
                            f"{C.data_edit_note}{b.callback_data.removeprefix(C.data_open_note)}"
                        )
                        b.text = b.text.replace(C.note_button_emoji, "✏️").replace("»", " ")

            btn.inline_keyboard[0] = [
                {
                    "text": "❌ Отмена                                                                                                                ",
                    "callback_data": f"{C.data_open_folder}{folder_id}",
                }
            ]

            await bot.edit_message_text(
                text=f"Выберите {C.note_button_emoji} заметку для редактирования",
                chat_id=user_id,
                message_id=message_id,
                reply_markup=btn,
            )

        case C.data_tips_off:
            await callback_query.answer(text="Скоро", show_alert=True)

        case C.data_new_notification:
            await callback_query.answer(text="Скоро", show_alert=True)

        case C.data_ok_message:
            await bot.delete_message(chat_id=user_id, message_id=message_id)
            schedule.delete_job(job_id=f"{C.job_id_from_message}{message_id}")

    if data.startswith(C.data_open_folder):
        folder_id = data.removeprefix(C.data_open_folder)
        folder = await Folder(id=folder_id).connect()
        await func.display_notes_keyboard(user_id=user_id, message_id=message_id, folder=folder)
        await db.set_status(user_id=user_id, new_status=C.status_empty)
        if not folder.notes:
            await callback_query.answer(
                text="Чтобы создать новую заметку, нажмите\n\n➕ Создать", show_alert=True
            )

    if data.startswith(C.data_open_resend_folder):
        folder_id = data.removeprefix(C.data_open_resend_folder)
        folder = await Folder(id=folder_id).connect()
        await func.display_notes_keyboard(
            user_id=user_id, message_id=message_id, folder=folder, is_reply=True
        )
        await db.set_status(user_id=user_id, new_status=C.status_empty)
        if not folder.notes:
            await callback_query.answer(
                text="Чтобы создать новую заметку, нажмите\n\n➕ Создать", show_alert=True
            )

    elif data.startswith(C.data_open_note):
        note_id = data.removeprefix(C.data_open_note)
        note = await Note(id=note_id).connect()

        await db.set_status(user_id=user_id, new_status=f"{C.status_updating_note}{note_id}")
        if note.content == C.default_note_content:
            await func.display_note(
                user_id=user_id,
                message_id=message_id,
                note=note,
                new_message_id_to_reply=note.message_id,
                first_time=True,
            )
            await callback_query.answer(
                text="Чтобы обновить текст заметки, отправьте сообщение", show_alert=True
            )
        else:
            await func.display_note(
                user_id=user_id,
                message_id=message_id,
                note=note,
                new_message_id_to_reply=note.message_id,
            )

    elif data.startswith(C.data_new_note):
        folder_id = data.removeprefix(C.data_new_note)
        note = Note(folder_id=folder_id)
        await note.connect()
        await callback_query.answer(text="Напишите имя заметки", show_alert=True)
        await func.display_notes_keyboard(user_id=user_id, message_id=message_id, folder_id=folder_id)
        await db.set_status(user_id=user_id, new_status=f"{C.status_updating_note_title}{note.id}")

    elif data.startswith(C.data_edit_folder):
        folder_id = data.removeprefix(C.data_edit_folder)
        btn = callback_query.message.reply_markup
        for kb in btn.inline_keyboard[1:]:
            for b in kb:
                folder_to_edit_data = f"{C.data_edit_folder}{folder_id}"

                if b.callback_data == folder_to_edit_data:
                    folder_text = b.text.replace("✏️", C.folder_button_emoji).rstrip()
                    break

        btn.inline_keyboard = [
            [
                {"text": "Удалить", "callback_data": f"{C.data_delete_folder}{folder_id}"},
                {
                    "text": "❌ Отмена                                                                                                                ",
                    "callback_data": C.data_see_folders,
                },
            ],
        ]

        await db.set_status(user_id=user_id, new_status=f"{C.status_updating_folder_name}{folder_id}")

        await bot.edit_message_text(
            text=f"<b>Папка <u>{folder_text}:</u> Редактирование</b>\n\nНапишите новое имя папки...",
            chat_id=user_id,
            message_id=message_id,
            reply_markup=btn,
        )

    elif data.startswith(C.data_delete_folder):
        folder_id = data.removeprefix(C.data_delete_folder)
        btn = await buttons.assemble_are_you_sure(folder_id=folder_id)

        await bot.edit_message_text(
            text="‼️Внимание‼️\n\nПри удалении папки, все ваши заметки, находящиеся внутри папки, также удалятся, вы уверены?",
            chat_id=user_id,
            message_id=message_id,
            reply_markup=btn,
        )

    elif data.startswith(C.data_sure_delete_folder):
        folder_id = data.removeprefix(C.data_sure_delete_folder)
        await db.delete_folder(folder_id=folder_id)
        await func.upd_folders_keyboard(user_id=user_id, message_id=message_id)

    elif data.startswith(C.data_edit_note):
        note_id = data.removeprefix(C.data_edit_note)
        btn = callback_query.message.reply_markup
        for kb in btn.inline_keyboard[1:]:
            for b in kb:
                folder_to_edit_data = f"{C.data_edit_note}{note_id}"
                dat = b.callback_data
                if dat == folder_to_edit_data:
                    note_text = b.text.replace("✏️", C.note_button_emoji).rstrip()
                elif dat.startswith(C.data_open_folder):
                    folder_id = dat.removeprefix(C.data_open_folder)

        btn.inline_keyboard = [
            [
                {"text": "Удалить", "callback_data": f"{C.data_delete_note}{note_id}_{folder_id}"},
                {
                    "text": "❌ Отмена                                                                                                                ",
                    "callback_data": f"{C.data_open_folder}{folder_id}",
                },
            ],
        ]
        await db.set_status(user_id=user_id, new_status=f"{C.status_updating_note_title}{note_id}")
        await bot.edit_message_text(
            text=f"<b>Заметка <u>{note_text}:</u> Редактирование</b>\n\nНапишите новый загловок заметки...",
            chat_id=user_id,
            message_id=message_id,
            reply_markup=btn,
        )

    elif data.startswith(C.data_delete_note):
        _, note_id, folder_id = data.split("_")

        btn = await buttons.assemble_are_you_sure(note_id=note_id, folder_id=folder_id)

        await bot.edit_message_text(
            text="Вы уверены?", chat_id=user_id, message_id=message_id, reply_markup=btn
        )

    elif data.startswith(C.data_sure_delete_note):
        _, note_id, folder_id = data.split("_")
        await db.delete_note(note_id=note_id)
        await func.display_notes_keyboard(user_id=user_id, message_id=message_id, folder_id=folder_id)

    elif data.startswith(C.data_set_language):
        new_language = data.removeprefix(C.data_set_language)
        await callback_query.answer(text="Скоро", show_alert=True)
