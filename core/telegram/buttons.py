from ..backend import constants as C
from . import functions as func
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from random import shuffle

menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⚙️ Настройки                                                                                         ",
                callback_data=C.data_see_settings,
            ),
            InlineKeyboardButton(
                text=f"{C.storage_button_emoji} Папки »",
                callback_data=C.data_see_folders,
            ),
        ],
        [
            InlineKeyboardButton(
                text="📅 Напоминание",
                callback_data=C.data_new_notification,
            ),
            InlineKeyboardButton(
                text="☕",
                url=C.donation_url,
            ),
        ],
    ]
)


ok = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👍 Понятно                                                                   ",
                callback_data=C.data_ok_message,
            ),
        ],
    ]
)


settings = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🌎 Язык 🇷🇺",
                callback_data="set language=RU",
                # 🇺🇸
            ),
            InlineKeyboardButton(
                text="Выключить подсказки",
                callback_data=C.data_tips_off,
            )
            # InlineKeyboardButton(
            #     text="Включить подсказки",
            #     callback_data="tips on"
            # )
            #
            # folders row_width
            # notes row_width
            #
        ],
        [
            InlineKeyboardButton(
                text="« Назад                                                                                                       ",
                callback_data=C.data_to_main_menu,
            )
        ],
    ]
)


async def assemble_single_note_kb(folder_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="« Назад                                ",
                    # Стандартная длина для кнопки, равна максимальной длине сообщения
                    callback_data=f"{C.data_open_resend_folder}{folder_id}",
                ),
            ]
        ]
    )


async def assemble_are_you_sure(folder_id: int = None, note_id: int = None):
    if note_id:
        to_del = f"{C.data_sure_delete_note}{note_id}_{folder_id}"
        data = f"{C.data_open_folder}{folder_id}"
    else:
        to_del = f"{C.data_sure_delete_folder}{folder_id}"
        data = C.data_see_folders

    No_No_Yes = [
        [
            InlineKeyboardButton(
                text="Нет                                                                                                                ",
                callback_data=data,
            )
        ],
        [InlineKeyboardButton(text="Ни в коем случае", callback_data=data)],
        [InlineKeyboardButton(text="Да", callback_data=to_del)],
    ]
    shuffle(No_No_Yes)

    return InlineKeyboardMarkup(inline_keyboard=No_No_Yes)


# create_what = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [
#             InlineKeyboardButton(text="Папку", callback_data=C.data_new_folder),
#             InlineKeyboardButton(text="Заметку", callback_data="new note"),
#         ],
#     ]
# )


def assemble_folder_kb(folders):
    buttons_list = []
    if len(folders) > 0:
        buttons_list.append(
            [
                InlineKeyboardButton(
                    text="« Меню                                                                                                                                                                      ",
                    callback_data=C.data_to_main_menu,
                ),
                InlineKeyboardButton(text="➕ Создать", callback_data=C.data_new_folder),
                InlineKeyboardButton(text="✏️ Изменить", callback_data=C.data_edit_folders),
            ]
        )

        keyboard_rows = [
            folders[i : i + C.default_folders_row_width]
            for i in range(0, len(folders), C.default_folders_row_width)
        ]

        for row in keyboard_rows:
            buttons_list.append(
                [
                    InlineKeyboardButton(
                        text=f"{C.folder_button_emoji} {folder.name} »",
                        callback_data=f"{C.data_open_folder}{folder.id}",
                    )
                    for folder in row
                ]
            )

    else:
        buttons_list.append(
            [
                InlineKeyboardButton(
                    text="« Меню                                                                                                                                                                      ",
                    callback_data=C.data_to_main_menu,
                ),
                InlineKeyboardButton(text="➕ Создать", callback_data=C.data_new_folder),
                InlineKeyboardButton(text=" ", callback_data=C.data_pass),
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons_list)


def assemble_notes_kb(notes, folder_id):
    buttons_list = []
    if len(notes) > 0:
        buttons_list.append(
            [
                InlineKeyboardButton(
                    text="« Папки                                                                                                                                                                      ",
                    callback_data=C.data_see_folders,
                ),
                InlineKeyboardButton(text="➕ Создать", callback_data=f"{C.data_new_note}{folder_id}"),
                InlineKeyboardButton(text="✏️ Изменить", callback_data=C.data_edit_notes),
            ]
        )

        keyboard_rows = [
            {"text": f"{C.note_button_emoji} {b.title} »", "callback_data": f"{C.data_open_note}{b.id}"}
            for b in notes
        ]

        row = []
        for button in keyboard_rows:
            row.append(button)
            if len(row) == C.default_notes_row_width:
                buttons_list.append(row)
                row = []

        if row:
            buttons_list.append(row)

    else:
        buttons_list.append(
            [
                InlineKeyboardButton(
                    text="« Папки                                                                                                                                                                      ",
                    callback_data=C.data_see_folders,
                ),
                InlineKeyboardButton(text="➕ Создать", callback_data=f"{C.data_new_note}{folder_id}"),
                InlineKeyboardButton(text=" ", callback_data=C.data_pass),
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons_list)
