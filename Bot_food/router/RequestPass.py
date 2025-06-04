from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router
from datetime import datetime
from Bot_food.config import CHAT_ID_GENERAL
import logging

router = Router()

logger = logging.getLogger(__name__)


# Состояния
class RequestPass(StatesGroup):
    organization = State()
    full_name = State()
    phone = State()
    department = State()
    position = State()


# Главное меню
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


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    username = message.from_user.username
    greeting = (
        f"Привет, {username}! Выберите действие:"
        if username
        else "Привет! Выберите действие:"
    )
    await message.answer(greeting, reply_markup=main_menu)


@router.message(Command("getid"))
async def get_chat_id(message: types.Message):
    await message.answer(f"Ваш chat_id: {message.chat.id}")


@router.message(lambda message: message.text == "Заявка на пропуск")
async def request_pass(message: types.Message, state: FSMContext):
    await state.set_state(RequestPass.organization)
    await message.answer("Укажите организацию:")


@router.message(RequestPass.organization)
async def process_organization(message: types.Message, state: FSMContext):
    await state.update_data(organization=message.text)
    await state.set_state(RequestPass.full_name)
    await message.answer("Укажите полное ФИО:")


@router.message(RequestPass.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(RequestPass.phone)
    await message.answer("Укажите номер телефона после +7:")


@router.message(RequestPass.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(RequestPass.department)
    await message.answer("Укажите ваш отдел:")


@router.message(RequestPass.department)
async def process_department(message: types.Message, state: FSMContext):
    await state.update_data(department=message.text)
    await state.set_state(RequestPass.position)
    await message.answer("Укажите вашу должность:")


@router.message(RequestPass.position)
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    data = await state.get_data()

    user = message.from_user
    username = user.username or f"{user.first_name} {user.last_name}".strip()
    if not username:
        username = "Пользователь"
    user_info = f"@{username} (ID: {user.id})"

    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")

    text = (
        f"📋 *Заявка на пропуск*\n"
        f"👤 Отправитель: {user_info}\n"
        f"🏢 Организация: {data['organization']}\n"
        f"📝 ФИО: {data['full_name']}\n"
        f"📞 Телефон: +7{data['phone']}\n"
        f"📂 Отдел: {data['department']}\n"
        f"💼 Должность: {data.get('position', 'Не указано')}\n"
        f"🕒 *Дата подачи:* {timestamp}"
    )

    try:
        await message.bot.send_message(
            CHAT_ID_GENERAL, text, parse_mode="Markdown", disable_web_page_preview=True
        )
        await message.answer(
            "✅ Ваша заявка на пропуск отправлена!\n\n"
            "⏳ Срок готовности: *1–2 рабочих дня*\n"
            "📍 Забрать пропуск можно в офисе по адресу: *ул. Миллионная, д.6*\n"
            "Обратитесь к офис-менеджеру.",
            parse_mode="Markdown",
            reply_markup=main_menu,
        )
        logger.info(f"Заявка на пропуск от пользователя {user.id} успешно отправлена.")
    except Exception as e:
        logger.error(f"Ошибка при отправке заявки на пропуск: {e}")
        await message.answer(
            "❗ Произошла ошибка при отправке заявки. Попробуйте позже."
        )
    finally:
        await state.clear()
