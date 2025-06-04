import logging
import re
import os
import tempfile
from enum import Enum
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, Message, ReplyKeyboardMarkup,
    KeyboardButton, PhotoSize
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from Bot_food.config import CHAT_ID_OFFICE_COURIER  # int

# --- Настройка логгера ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# --- Инициализация роутера ---
router = Router()

# --- FSM: состояния заявки ---
class CourierRequest(StatesGroup):
    from_address = State()
    sender_info = State()
    to_address = State()
    recipient_info = State()
    item_description = State()
    deadline = State()
    comment = State()
    attachment = State()
    confirmation = State()

# --- Enum для callback_data ---
class Callbacks(str, Enum):
    CONFIRM = "confirm_request"
    CANCEL = "cancel_request"

# --- Клавиатуры ---
attach_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📎 Приложить файл"), KeyboardButton(text="❌ Пропустить")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

confirm_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=Callbacks.CONFIRM.value),
            InlineKeyboardButton(text="❌ Отменить", callback_data=Callbacks.CANCEL.value),
        ]
    ]
)

# --- Экранирование MarkdownV2 ---
def escape_md_v2(text: str) -> str:
    if not text:
        return "-"
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!\\])', r'\\\1', text)

# --- Обработчик команды /chatid ---
@router.message(Command("chatid"))
async def chat_id_handler(message: Message):
    await message.answer(f"Этот чат имеет ID: `{message.chat.id}`", parse_mode="Markdown")

# --- Старт заявки ---
@router.message(F.text == "Заявка на офисного курьера")
async def start_request(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} начал оформление заявки.")
    await state.set_state(CourierRequest.from_address)
    await state.update_data(user_id=message.from_user.id)
    await message.answer("Заявки оформляются за 1 день и более, "
                         "доставка по СПБ и ближайшей области. "
                         "Для того, чтобы создать заявку на офисного курьера "
                         "ответьте на следующие вопросы:.\n\n📍 Введите адрес (откуда забрать):")

# --- Обработчики FSM состояний ---
@router.message(CourierRequest.from_address)
async def process_from_address(message: Message, state: FSMContext):
    await state.update_data(from_address=message.text)
    await state.set_state(CourierRequest.sender_info)
    await message.answer("📨 Введите данные отправителя:")

@router.message(CourierRequest.sender_info)
async def process_sender_info(message: Message, state: FSMContext):
    await state.update_data(sender_info=message.text)
    await state.set_state(CourierRequest.to_address)
    await message.answer("👜 Введите адрес доставки (куда):")

@router.message(CourierRequest.to_address)
async def process_to_address(message: Message, state: FSMContext):
    await state.update_data(to_address=message.text)
    await state.set_state(CourierRequest.recipient_info)
    await message.answer("👤 Введите данные получателя:")

@router.message(CourierRequest.recipient_info)
async def process_recipient_info(message: Message, state: FSMContext):
    await state.update_data(recipient_info=message.text)
    await state.set_state(CourierRequest.item_description)
    await message.answer("📦 Что нужно доставить?")

@router.message(CourierRequest.item_description)
async def process_item_description(message: Message, state: FSMContext):
    await state.update_data(item_description=message.text)
    await state.set_state(CourierRequest.deadline)
    await message.answer("⏒ Крайний срок доставки:")

@router.message(CourierRequest.deadline)
async def process_deadline(message: Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await state.set_state(CourierRequest.comment)
    await message.answer("💬 Комментарий: (требуется пропуск, позвонить заранее и т.д.):")

@router.message(CourierRequest.comment)
async def process_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(CourierRequest.attachment)
    await message.answer("📎 Хотите приложить файл?", reply_markup=attach_keyboard)

# --- Обработка вложений ---

@router.message(CourierRequest.attachment, F.document)
async def handle_document(message: Message, state: FSMContext):
    await state.update_data(file_id=message.document.file_id, file_type="document")
    await message.answer("📎 Файл получен.")
    await prepare_confirmation(message, state)

@router.message(CourierRequest.attachment, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    photo: PhotoSize = message.photo[-1]
    await state.update_data(file_id=photo.file_id, file_type="photo")
    await message.answer("🖼 Фото получено.")
    await prepare_confirmation(message, state)

@router.message(CourierRequest.attachment, F.text.in_(["❌ Пропустить"]))
async def skip_attachment(message: Message, state: FSMContext):
    await prepare_confirmation(message, state)

@router.message(CourierRequest.attachment, F.text.in_(["📎 Приложить файл"]))
async def ask_for_attachment(message: Message):
    await message.answer("📤 Отправьте фото или документ одним сообщением:")

@router.message(CourierRequest.attachment)
async def invalid_attachment(message: Message):
    await message.answer("❗ Отправьте фото, документ или нажмите 'Пропустить'.")

# --- Утилита для скачивания файла ---
async def download_file(bot, file_id) -> str:
    file = await bot.get_file(file_id)
    file_path = file.file_path
    suffix = os.path.splitext(file_path)[-1] or ""
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    await bot.download_file(file_path, tmp_file.name)
    tmp_file.close()
    return tmp_file.name

# --- Формируем сообщение подтверждения ---
async def prepare_confirmation(message: Message, state: FSMContext):
    data = await state.get_data()

    def safe(key):
        return escape_md_v2(data.get(key, "-"))

    summary = (
        "🤖 *BotCorp CourierBot*\n"
        "📦 *Новая заявка на офисного курьера*\n"
        f"📍 *Откуда:* {safe('from_address')}\n"
        f"📨 *Отправитель:* {safe('sender_info')}\n"
        f"👜 *Куда:* {safe('to_address')}\n"
        f"👤 *Получатель:* {safe('recipient_info')}\n"
        f"📦 *Что доставить:* {safe('item_description')}\n"
        f"⏒ *Срок:* {safe('deadline')}\n"
        f"💬 *Комментарий:* {safe('comment')}\n"
    )

    logger.debug("Сформировано сообщение подтверждения:\n%s", summary)
    await state.update_data(summary_text=summary)
    await state.set_state(CourierRequest.confirmation)
    await message.answer(summary, reply_markup=confirm_keyboard, parse_mode="MarkdownV2")

# --- Обработка подтверждения ---
@router.callback_query(F.data == Callbacks.CONFIRM.value)
async def confirm_request(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    logger.info(f"Заявка подтверждена пользователем {user_id}")
    logger.info(f"Отправка заявки в чат {CHAT_ID_OFFICE_COURIER}")

    try:
        # Отправляем текст заявки
        await callback.bot.send_message(
            CHAT_ID_OFFICE_COURIER,
            data.get("summary_text", "-"),
            parse_mode="MarkdownV2"
        )

        file_id = data.get("file_id")
        file_type = data.get("file_type")

        if file_id and file_type in ("document", "photo"):
            local_path = await download_file(callback.bot, file_id)
            caption = "📎 Вложение к заявке"

            try:
                with open(local_path, "rb") as f:
                    if file_type == "document":
                        await callback.bot.send_document(
                            CHAT_ID_OFFICE_COURIER,
                            document=f,
                            caption=caption
                        )
                    elif file_type == "photo":
                        await callback.bot.send_photo(
                            CHAT_ID_OFFICE_COURIER,
                            photo=f,
                            caption=caption
                        )
            finally:
                os.remove(local_path)
        else:
            logger.warning("Вложение не найдено или тип неизвестен")

        await callback.message.answer("✅ Заявка успешно отправлена!")
        await state.clear()

    except Exception:
        logger.exception("Ошибка при отправке заявки")
        await callback.message.answer("❗ Ошибка при отправке заявки. Попробуйте позже.")

# --- Обработка отмены ---
@router.callback_query(F.data == Callbacks.CANCEL.value)
async def cancel_request(callback: CallbackQuery, state: FSMContext):
    user_id = (await state.get_data()).get("user_id")
    logger.info(f"Пользователь {user_id} отменил оформление заявки.")
    await callback.message.answer("❌ Заявка отменена.")
    await state.clear()
