import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove # клавиатуру можно сделать поинтересней
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
    document_name = State()
    spb_recipient = State()
    attachments = State()

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

    # Формируем текст для отправки
    text = (f"📋 Заявка на пропуск\n"
            f"Организация: {data['organization']}\n"
            f"ФИО: {data['full_name']}\n"
            f"Телефон: +7{data['phone']}\n"
            f"Отдел: {data['department']}\n"
            f"Должность: {data.get('position', 'Не указано')}\n"
            f"Отправитель: {message.from_user.username}")

    try:
        # Проверяем отправку сообщения
        await bot.send_message(CHAT_ID_GENERAL, text)
        await message.answer("Готово! Ваша заявка на пропуск отправлена, срок готовности: 1-2 дня.\n"
                             "Забрать пропуск можно в офисе по адресу: ул. Миллионная, д.6\n"
                             "Для этого обратитесь, пожалуйста, к офис-менеджеру.")
    except Exception as e:
        # Логирование и сообщение об ошибке
        print(f"Не удалось отправить сообщение в чат {CHAT_ID_GENERAL}: {e}")
        await message.answer("Произошла ошибка при отправке заявки. Попробуйте позже.")
    finally:
        # Завершаем состояние
        await state.clear()


# Заявка на офисного курьера
@dp.message(lambda message: message.text == "Заявка на офисного курьера")
async def courier_request(message: types.Message, state: FSMContext):
    await state.set_state(CourierRequest.from_address)
    await message.answer("Заявки оформляются за 1 день и более, доставка по СПБ и ближайшей области. "
                         "Для того, чтобы создать заявку на офисного курьера ответьте на следующие вопросы:\n"
                         "Адрес (откуда):")

@dp.message(CourierServiceRequest.recipient_name)
async def process_recipient_name(message: types.Message, state: FSMContext):
    await state.update_data(recipient_name=message.text)
    await state.set_state(CourierServiceRequest.recipient_address)
    await message.answer("Введите адрес (куда доставить / откуда забираем):")

@dp.message(CourierServiceRequest.recipient_address)
async def process_recipient_address(message: types.Message, state: FSMContext):
    await state.update_data(recipient_address=message.text)
    await state.set_state(CourierServiceRequest.recipient_phone)
    await message.answer("Введите телефон получателя / отправителя:")

@dp.message(CourierServiceRequest.recipient_phone)
async def process_recipient_phone(message: types.Message, state: FSMContext):
    await state.update_data(recipient_phone=message.text)
    await state.set_state(CourierServiceRequest.document_name)
    await message.answer("Введите наименование документов:")

@dp.message(CourierServiceRequest.document_name)
async def process_document_name(message: types.Message, state: FSMContext):
    await state.update_data(document_name=message.text)
    await state.set_state(CourierServiceRequest.deadline)
    await message.answer("Введите крайний срок отправки / забора документов:")

@dp.message(CourierServiceRequest.deadline)
async def process_deadline(message: types.Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await state.set_state(CourierServiceRequest.comment)
    await message.answer("Введите комментарий (если есть):")

@dp.message(CourierServiceRequest.comment)
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)

    data = await state.get_data()

    summary = (
        f"📦 **Заявка на курьерскую службу**\n"
        f"Тип: {data.get('service_type')}\n"
        f"Имя: {data.get('recipient_name')}\n"
        f"Адрес: {data.get('recipient_address')}\n"
        f"Телефон: {data.get('recipient_phone')}\n"
        f"Документы: {data.get('document_name')}\n"
        f"Срок: {data.get('deadline')}\n"
        f"Комментарий: {data.get('comment')}\n"
    )

    # Если "Мы получаем", добавляем имя получателя в СПБ
    if data.get("service_type") == "получение":
        await state.set_state(CourierServiceRequest.spb_recipient)
        await message.answer("Введите имя получателя в СПБ (кому передать):")
    else:
        await message.answer(summary)
        await state.clear()  # Очищаем состояние

@dp.message(CourierServiceRequest.spb_recipient)
async def process_spb_recipient(message: types.Message, state: FSMContext):
    await state.update_data(spb_recipient=message.text)
    data = await state.get_data()

    summary = (
        f"📦 **Заявка на курьерскую службу**\n"
        f"Тип: {data.get('service_type')}\n"
        f"Имя отправителя: {data.get('recipient_name')}\n"
        f"Адрес: {data.get('recipient_address')}\n"
        f"Телефон: {data.get('recipient_phone')}\n"
        f"Документы: {data.get('document_name')}\n"
        f"Срок: {data.get('deadline')}\n"
        f"Комментарий: {data.get('comment')}\n"
        f"Получатель в СПБ: {data.get('spb_recipient')}\n"
    )

    await message.answer(summary)
    await state.clear()  # Очищаем состояние


# Заявка на курьерскую службу
courier_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мы отправляем")],
        [KeyboardButton(text="Мы получаем")]
    ],
    resize_keyboard=True,  # Автоматическое изменение размера клавиатуры
    one_time_keyboard=True  # Клавиатура исчезнет после нажатия кнопки
)

@dp.message(lambda message: message.text == "Заявка на курьерскую службу (KSE)")
async def courier_service_request(message: types.Message, state: FSMContext):
    await state.set_state(CourierServiceRequest.service_type)
    await message.answer("Выберите тип курьерской службы:", reply_markup=courier_keyboard)

@dp.message(lambda message: message.text in ["Мы отправляем", "Мы получаем"])
async def process_courier_choice(message: types.Message, state: FSMContext):
    choice = "отправка" if message.text == "Мы отправляем" else "получение"
    await state.update_data(service_type=choice)

    await state.set_state(CourierServiceRequest.recipient_name)
    if choice == "отправка":
        await message.answer("Введите имя получателя:", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Введите имя отправителя:", reply_markup=types.ReplyKeyboardRemove())



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
