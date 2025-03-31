import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton # клавиатуру можно сделать поинтересней
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import CHAT_ID_GENERAL, CHAT_ID_COURIER
from my_token import TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Определение состояний
class RequestPass(StatesGroup):
    organization = State()
    full_name = State()
    phone = State()
    department = State()
    position = State()

class CourierRequest(StatesGroup):
    from_address = State()
    sender_info = State()
    to_address = State()
    recipient_info = State()
    item_description = State()
    deadline = State()
    comment = State()
    attachments = State()

class CourierServiceRequest(StatesGroup):
    service_type = State()
    recipient_name = State()
    recipient_address = State()
    recipient_phone = State()
    item_description = State()
    deadline = State()
    comment = State()
    sender_name = State()
    sender_address = State()
    sender_phone = State()

class MeetingRequest(StatesGroup):
    date = State()
    time = State()
    details = State()

class StationeryRequest(StatesGroup):
    urgency = State()
    item_list = State()

class ProblemReport(StatesGroup):
    problem_type = State()
    description = State()

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
    resize_keyboard=True
)

# main_menu = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [InlineKeyboardButton(text="Заявка на пропуск", callback_data="request_pass")],
#         [InlineKeyboardButton(text="Заявка на офисного курьера", callback_data="office_courier")],
#         [InlineKeyboardButton(text="Заявка на курьерскую службу (KSE)", callback_data="courier_service")],
#         [InlineKeyboardButton(text="Встретить гостя, курьера и тд", callback_data="meet_guest")],
#         [InlineKeyboardButton(text="Заказ канцелярии", callback_data="stationery_order")],
#         [InlineKeyboardButton(text="Сообщить о проблеме", callback_data="report_problem")],
#     ]
# )

# Обработчик команды "/start"
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Получаем ник пользователя
    username = message.from_user.username
    if username:
        greeting = f"Привет, {username}! Выберите действие:"
    else:
        greeting = "Привет! Выберите действие:"

    await message.answer(greeting, reply_markup=main_menu)

# Заявка на пропуск
@dp.message(lambda message: message.text == "Заявка на пропуск")
async def request_pass(message: types.Message, state: FSMContext):
    await state.set_state(RequestPass.organization)
    await message.answer("Укажите организацию:")

@dp.message(RequestPass.organization)
async def process_organization(message: types.Message, state: FSMContext):
    await state.update_data(organization=message.text)
    await state.set_state(RequestPass.full_name)
    await message.answer("Укажите полное ФИО:")

@dp.message(RequestPass.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(RequestPass.phone)
    await message.answer("Укажите номер телефона после +7:")

@dp.message(RequestPass.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(RequestPass.department)
    await message.answer("Укажите ваш отдел:")

@dp.message(RequestPass.department)
async def process_department(message: types.Message, state: FSMContext):
    await state.update_data(department=message.text)
    await state.set_state(RequestPass.position)
    await message.answer("Укажите вашу должность:")

@dp.message(RequestPass.position)
async def process_position(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = (f"📋 Заявка на пропуск\n"
            f"Организация: {data['organization']}\n"
            f"ФИО: {data['full_name']}\n"
            f"Телефон: +7{data['phone']}\n"
            f"Отдел: {data['department']}\n"
            f"Должность: {data.get('position', 'Не указано')}\n"
            f"Отправитель: {message.from_user.username}")
    await bot.send_message(CHAT_ID_GENERAL, text)
    await message.answer("Готово! Ваша заявка на пропуск отправлена, срок готовности: 1-2 дня.\n"
                         "Забрать пропуск можно в офисе по адресу: ул. Миллионная, д.6\n"
                         "Для этого обратитесь, пожалуйста, к офис-менеджеру.")
    await state.clear()

# Заявка на офисного курьера
@dp.message(lambda message: message.text == "Заявка на офисного курьера")
async def courier_request(message: types.Message, state: FSMContext):
    await state.set_state(CourierRequest.from_address)
    await message.answer("Заявки оформляются за 1 день и более, доставка по СПБ и ближайшей области. "
                         "Для того, чтобы создать заявку на офисного курьера ответьте на следующие вопросы:\n"
                         "Адрес (откуда):")

@dp.message(CourierRequest.from_address)
async def process_from_address(message: types.Message, state: FSMContext):
    await state.update_data(from_address=message.text)
    await state.set_state(CourierRequest.sender_info)
    await message.answer("Отправитель и номер телефона:")

@dp.message(CourierRequest.sender_info)
async def process_sender_info(message: types.Message, state: FSMContext):
    await state.update_data(sender_info=message.text)
    await state.set_state(CourierRequest.to_address)
    await message.answer("Куда (адрес):")

@dp.message(CourierRequest.to_address)
async def process_to_address(message: types.Message, state: FSMContext):
    await state.update_data(to_address=message.text)
    await state.set_state(CourierRequest.recipient_info)
    await message.answer("Получатель и номер телефона:")

@dp.message(CourierRequest.recipient_info)
async def process_recipient_info(message: types.Message, state: FSMContext):
    await state.update_data(recipient_info=message.text)
    await state.set_state(CourierRequest.item_description)
    await message.answer("Наименование (документы или груз):")

@dp.message(CourierRequest.item_description)
async def process_item_description(message: types.Message, state: FSMContext):
    await state.update_data(item_description=message.text)
    await state.set_state(CourierRequest.deadline)
    await message.answer("Крайний срок доставки:")

@dp.message(CourierRequest.deadline)
async def process_deadline(message: types.Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await state.set_state(CourierRequest.comment)
    await message.answer("Комментарий: (требуется пропуск, позвонить заранее и т.д.):")

@dp.message(CourierRequest.comment)
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(CourierRequest.attachments)
    await message.answer("Требуется вложить изображения/документы?")

@dp.message(CourierRequest.attachments)
async def process_attachments(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = (f"📦 Заявка на офисного курьера\n"
            f"Откуда: {data['from_address']}\n"
            f"Отправитель: {data['sender_info']}\n"
            f"Куда: {data['to_address']}\n"
            f"Получатель: {data['recipient_info']}\n"
            f"Документы/Груз: {data['item_description']}\n"
            f"Крайний срок доставки: {data['deadline']}\n"
            f"Комментарий: {data['comment']}\n"
            f"Отправитель: {message.from_user.username}")
    await bot.send_message(chat_id=CHAT_ID_COURIER, text="Ваш текст")
    await message.answer("Готово! Ваша заявка принята.")
    await state.clear()

# Заявка на курьерскую службу
@dp.message(lambda message: message.text == "Заявка на курьерскую службу (KSE)")
async def courier_service_request(message: types.Message, state: FSMContext):
    await state.set_state(CourierServiceRequest.service_type)
    await message.answer("Тип курьерской службы:\nВыберите: Мы отправляем или Мы получаем")

@dp.message(CourierServiceRequest.service_type)
async def process_service_type(message: types.Message, state: FSMContext):
    await state.update_data(service_type=message.text)
    if message.text == "Мы отправляем":
        await state.set_state(CourierServiceRequest.recipient_name)
        await message.answer("Имя получателя:")
    elif message.text == "Мы получаем":
        await state.set_state(CourierServiceRequest.sender_name)
        await message.answer("Имя отправителя:")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
