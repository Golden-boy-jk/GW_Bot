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

router = Router()

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

    summary = (
        f"📋 *Заявка на встречу гостя/курьера:*\n"
        f"🗓 Дата: {data['date']}\n"
        f"⏰ Время: {data['time']}\n"
        f"📌 Требования: {data['requirements']}"
    )

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
    if callback.data == "confirm_meeting":
        await callback.message.answer(
            "✅ Заявка подтверждена и отправлена!", reply_markup=return_main_menu
        )
        # Можешь отправить админу
    else:
        await callback.message.answer(
            "❌ Заявка отменена.", reply_markup=return_main_menu
        )

    await state.clear()
    await callback.answer()
