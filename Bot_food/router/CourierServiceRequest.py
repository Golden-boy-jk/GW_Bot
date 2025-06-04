import logging
from enum import Enum
from datetime import datetime

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from Bot_food.config import CHAT_ID_OFFICE_COURIER, CHAT_ID_KSE

router = Router()


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Заявка на пропуск")],
        [KeyboardButton(text="Заявка на офисного курьера")],
        [KeyboardButton(text="Заявка на курьерскую службу (KSE)")],
        [KeyboardButton(text="Встретить гостя, курьера и тд")],
        [KeyboardButton(text="Заказ канцелярии")],
        [KeyboardButton(text="Сообщить о проблеме")],
    ],
    resize_keyboard=True,
)

courier_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мы отправляем")],
        [KeyboardButton(text="Мы получаем")],
    ],
    resize_keyboard=True,
)


class Callbacks(str, Enum):
    CONFIRM = "confirm_request"
    CANCEL = "cancel_request"


confirm_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", callback_data=Callbacks.CONFIRM
            ),
            InlineKeyboardButton(text="❌ Отменить", callback_data=Callbacks.CANCEL),
        ]
    ]
)


class CourierServiceRequest(StatesGroup):
    service_type = State()
    recipient_name = State()
    recipient_address = State()
    recipient_phone = State()
    document_name = State()
    item_description = State()
    deadline = State()
    comment = State()
    spb_recipient = State()


def escape_md_v2(text: str) -> str:
    escape_chars = r"_*\[\]()~`>#+\-=|{}.!\\"
    return "".join(f"\\{c}" if c in escape_chars else c for c in text or "-")


# --- Хендлеры ---


@router.message(lambda message: message.text == "Заявка на курьерскую службу (KSE)")
async def courier_service_request(message: types.Message, state: FSMContext):
    await state.set_state(CourierServiceRequest.service_type)
    await message.answer(
        "Внимание! Одна из точек (забор/отправка) "
        "– по-умолчанию офис в СПб (ул. Миллионная, д.6)."
        " Если вам нужно отправить документы в офис СПб – выберите «Мы получаем» "
        "и укажите адрес, откуда нужно забрать документы."
        " Если вам нужно получить документы из петербургского офиса – "
        "выберите «Мы отправляем»", reply_markup=courier_keyboard
    )


@router.message(CourierServiceRequest.service_type)
async def process_courier_choice(message: types.Message, state: FSMContext):
    choice = "отправка" if message.text == "Мы отправляем" else "получение"
    await state.update_data(service_type=choice)
    await state.set_state(CourierServiceRequest.recipient_name)
    await message.answer(
        "Введите имя получателя:"
        if choice == "отправка"
        else "Введите имя отправителя:",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(CourierServiceRequest.recipient_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(recipient_name=message.text)
    await state.set_state(CourierServiceRequest.recipient_address)
    await message.answer("Введите адрес:")


@router.message(CourierServiceRequest.recipient_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(recipient_address=message.text)
    await state.set_state(CourierServiceRequest.recipient_phone)
    await message.answer("Введите телефон:")


@router.message(CourierServiceRequest.recipient_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(recipient_phone=message.text)
    await state.set_state(CourierServiceRequest.document_name)
    await message.answer("Введите наименование документов:")


@router.message(CourierServiceRequest.document_name)
async def process_docs(message: types.Message, state: FSMContext):
    await state.update_data(document_name=message.text)
    await state.set_state(CourierServiceRequest.item_description)
    await message.answer("Что доставляется?")


@router.message(CourierServiceRequest.item_description)
async def process_item_description(message: types.Message, state: FSMContext):
    await state.update_data(item_description=message.text)
    await state.set_state(CourierServiceRequest.deadline)
    await message.answer("Крайний срок доставки:")


@router.message(CourierServiceRequest.deadline)
async def process_deadline(message: types.Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await state.set_state(CourierServiceRequest.comment)
    await message.answer("Комментарий (если есть):")


@router.message(CourierServiceRequest.comment)
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(CourierServiceRequest.spb_recipient)
    await message.answer("Получатель в СПБ (ФИО, адрес):")


@router.message(CourierServiceRequest.spb_recipient)
async def process_spb_recipient(message: types.Message, state: FSMContext):
    await state.update_data(spb_recipient=message.text)
    data = await state.get_data()

    summary_text = (
        f"*📦 Заявка на курьерскую службу*\n"
        f"*Тип:* {escape_md_v2(data.get('service_type'))}\n"
        f"*Имя:* {escape_md_v2(data.get('recipient_name'))}\n"
        f"*Адрес:* {escape_md_v2(data.get('recipient_address'))}\n"
        f"*Телефон:* {escape_md_v2(data.get('recipient_phone'))}\n"
        f"*Документы:* {escape_md_v2(data.get('document_name'))}\n"
        f"*Что доставляется:* {escape_md_v2(data.get('item_description'))}\n"
        f"*Срок:* {escape_md_v2(data.get('deadline'))}\n"
        f"*Комментарий:* {escape_md_v2(data.get('comment'))}\n"
        f"*Получатель в СПБ:* {escape_md_v2(data.get('spb_recipient'))}"
    )

    await state.update_data(summary_text=summary_text)
    await message.answer(
        summary_text, reply_markup=confirm_keyboard, parse_mode="MarkdownV2"
    )


@router.callback_query(lambda c: c.data in [Callbacks.CONFIRM, Callbacks.CANCEL])
async def handle_confirmation(callback: CallbackQuery, state: FSMContext):
    if callback.data == Callbacks.CONFIRM:
        await handle_kse_request_submission(callback, state)
    else:
        await callback.message.answer("❌ Заявка отменена.", reply_markup=main_menu)
        await state.clear()
        await callback.answer()


async def handle_kse_request_submission(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user

    service_type = data.get("service_type", "").lower()
    if service_type in ["отправка", "получение"]:
        chat_id = CHAT_ID_KSE
    else:
        chat_id = CHAT_ID_OFFICE_COURIER

    try:
        user_info = (
            f"👤 *Отправитель:*\n"
            f"• Имя: {escape_md_v2(user.full_name)}\n"
            f"• Username: {escape_md_v2(f'@{user.username}') if user.username else '—'}\n"
            f"• ID: `{user.id}`\n\n"
        )
        summary_text = data.get("summary_text", "Нет данных")

        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        full_text = (
            f"{user_info}"
            f"{summary_text}\n\n"
            f"🕒 *Заявка подана:* {escape_md_v2(timestamp)}"
        )

        await callback.bot.send_message(chat_id, full_text, parse_mode="MarkdownV2")
        await callback.message.answer(
            "✅ Заявка подтверждена и отправлена!", reply_markup=main_menu
        )
    except Exception as e:
        logging.exception("Ошибка при отправке заявки:")
        await callback.message.answer(
            f"❌ Ошибка при отправке заявки: {e}", reply_markup=main_menu
        )

    await state.clear()
    await callback.answer()
