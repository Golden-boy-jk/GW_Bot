from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from Bot_food.config import CHAT_ID_GENERAL
import logging
from datetime import datetime

router = Router()

# Логирование (по желанию)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Главное меню, возвращается после подтверждения/отмены
return_main_menu = ReplyKeyboardMarkup(
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


class MeetGuestRequest(StatesGroup):
    date = State()
    time = State()
    requirements = State()


@router.message(lambda message: message.text == "Встретить гостя, курьера и тд")
async def meet_guest(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} начал заявку на встречу гостя")
    await state.set_state(MeetGuestRequest.date)
    await message.answer(
        "🗓 Укажите дату встречи (ДД.ММ.ГГГГ):", reply_markup=ReplyKeyboardRemove()
    )


@router.message(MeetGuestRequest.date)
async def process_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(MeetGuestRequest.time)
    await message.answer("⏰ Укажите время встречи (ЧЧ:ММ):")


@router.message(MeetGuestRequest.time)
async def process_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(MeetGuestRequest.requirements)
    await message.answer("📌 Что именно требуется? Опишите подробно:")


@router.message(MeetGuestRequest.requirements)
async def process_requirements(message: types.Message, state: FSMContext):
    await state.update_data(requirements=message.text)
    data = await state.get_data()

    # Дата и время создания
    created_at = datetime.now().strftime("%d.%m.%Y %H:%M")

    summary = (
        f"📋 *Заявка на встречу гостя/курьера:*\n"
        f"🗓 Дата встречи: {data['date']}\n"
        f"⏰ Время встречи: {data['time']}\n"
        f"📌 Требования: {data['requirements']}\n\n"
        f"🕒 Заявка создана: {created_at}"
    )

    # Сохраняем текст и дату создания для дальнейшего использования
    await state.update_data(summary_text=summary)

    await message.answer(summary, parse_mode="Markdown")
    await message.answer(
        "Подтвердите или отмените заявку:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Подтвердить", callback_data="confirm_meeting"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Отменить", callback_data="cancel_meeting"
                    )
                ],
            ]
        ),
    )


@router.callback_query(lambda c: c.data in ["confirm_meeting", "cancel_meeting"])
async def handle_confirmation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # Закрываем "часики" в интерфейсе
    data = await state.get_data()
    user = callback.from_user

    full_name = (
        user.full_name or (f"{user.first_name or ''} {user.last_name or ''}").strip()
    )
    if not full_name:
        full_name = "—"

    username = f"@{user.username}" if user.username else "—"
    user_id = user.id

    user_info = (
        f"👤 *Отправитель:*\n"
        f"• Имя: {full_name}\n"
        f"• Username: {username}\n"
        f"• ID: `{user_id}`\n\n"
    )

    if callback.data == "confirm_meeting":
        try:
            full_text = user_info + data.get("summary_text", "Заявка без текста")
            await callback.bot.send_message(
                CHAT_ID_GENERAL, full_text, parse_mode="Markdown"
            )
            logger.info(
                f"Пользователь {user_id} подтвердил заявку и она отправлена в чат"
            )
            await callback.message.answer(
                "✅ Заявка подтверждена и отправлена!", reply_markup=return_main_menu
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке заявки пользователя {user_id}: {e}")
            await callback.message.answer(f"❗ Ошибка при отправке: {e}")
    else:
        logger.info(f"Пользователь {user_id} отменил заявку")
        await callback.message.answer(
            "❌ Заявка отменена.", reply_markup=return_main_menu
        )

    await state.clear()
