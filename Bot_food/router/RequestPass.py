from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router

from config import CHAT_ID_GENERAL  # импортируй токен здесь

router = Router()


class RequestPass(StatesGroup):
    organization = State()
    full_name = State()
    phone = State()
    department = State()
    position = State()


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
async def cmd_start(message: types.Message):
    username = message.from_user.username
    greeting = (
        f"Привет, {username}! Выберите действие:"
        if username
        else "Привет! Выберите действие:"
    )
    await message.answer(greeting, reply_markup=main_menu)


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
    data = await state.get_data()

    text = (
        f"📋 Заявка на пропуск\n"
        f"Организация: {data['organization']}\n"
        f"ФИО: {data['full_name']}\n"
        f"Телефон: +7{data['phone']}\n"
        f"Отдел: {data['department']}\n"
        f"Должность: {data.get('position', 'Не указано')}\n"
        f"Отправитель: {message.from_user.username}"
    )

    try:
        await message.bot.send_message(
            CHAT_ID_GENERAL, text
        )  # 👈 Вот тут важный момент
        await message.answer(
            "Готово! Ваша заявка на пропуск отправлена, срок готовности: 1–2 дня.\n"
            "Забрать пропуск можно в офисе по адресу: ул. Миллионная, д.6\n"
            "Для этого обратитесь, пожалуйста, к офис-менеджеру."
        )
    except Exception as e:
        print(f"Не удалось отправить сообщение в чат {CHAT_ID_GENERAL}: {e}")
        await message.answer("Произошла ошибка при отправке заявки. Попробуйте позже.")
    finally:
        await state.clear()
