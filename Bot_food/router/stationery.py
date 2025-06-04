import re
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from Bot_food.config import CHAT_ID_GENERAL
import logging
from datetime import datetime

router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Главное меню
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

# Callback константы
ORDER_URGENT = "order_type_urgent"
ORDER_REGULAR = "order_type_regular"


# Экранирование MarkdownV2
def escape_md(text: str) -> str:
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!\\])", r"\\\1", text)


# Состояния FSM
class OrderStationeryStates(StatesGroup):
    order_type = State()
    waiting_for_items = State()
    confirmation = State()


# Клавиатуры
def order_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Срочно", callback_data=ORDER_URGENT),
                InlineKeyboardButton(
                    text="Ближайшая доставка", callback_data=ORDER_REGULAR
                ),
            ]
        ]
    )


def confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить заказ", callback_data="confirm_order"
                ),
                InlineKeyboardButton(
                    text="❌ Отменить заказ", callback_data="cancel_order"
                ),
            ]
        ]
    )


# Старт заказа
@router.message(lambda message: message.text.lower() == "заказ канцелярии")
async def order_stationery(message: Message):
    await message.answer("Выберите тип заказа:", reply_markup=order_type_keyboard())


# Обработка выбора типа
@router.callback_query(lambda c: c.data in [ORDER_URGENT, ORDER_REGULAR])
async def handle_order_type(callback: CallbackQuery, state: FSMContext):
    await state.update_data(order_type=callback.data)
    await callback.message.edit_text(
        "Заказ осуществляется через компанию Комус.\n"
        "Вставьте артикул или перечислите необходимые товары для заказа:"
    )
    await state.set_state(OrderStationeryStates.waiting_for_items)
    await callback.answer()


# Получение списка товаров
@router.message(OrderStationeryStates.waiting_for_items)
async def receive_items(message: Message, state: FSMContext):
    await state.update_data(items=message.text)

    user_data = await state.get_data()
    order_type = user_data.get("order_type", "Не указан")
    items = escape_md(user_data.get("items", ""))

    user = message.from_user
    username = user.username
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    user_id = user.id

    user_info = f"@{username}" if username else f"{first_name} {last_name}".strip()
    if not user_info:
        user_info = "Пользователь"
    user_info += f" \\(ID: {user_id}\\)"
    user_info = escape_md(user_info)

    summary = (
        f"📦 *Новый заказ канцелярии*\n"
        f"*Пользователь:* {user_info}\n"
        f"*Тип заказа:* {'Срочный' if order_type == ORDER_URGENT else 'Обычный'}\n"
        f"*Товары:* {items}"
    )

    await message.answer(summary, parse_mode="MarkdownV2")
    await message.answer(
        "Подтвердите или отмените заказ:", reply_markup=confirmation_keyboard()
    )
    await state.set_state(OrderStationeryStates.confirmation)


# Подтверждение или отмена
@router.callback_query(lambda c: c.data in ["confirm_order", "cancel_order"])
async def handle_order_confirmation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    user = callback.from_user

    data = await state.get_data()
    order_type = data.get("order_type", "Не указан")
    items = escape_md(data.get("items", ""))

    username = user.username
    first_name = user.first_name or ""
    last_name = user.last_name or ""

    user_info = f"@{username}" if username else f"{first_name} {last_name}".strip()
    if not user_info:
        user_info = "Пользователь"
    user_info += f" \\(ID: {user_id}\\)"
    user_info = escape_md(user_info)

    timestamp = escape_md(datetime.now().strftime("%d.%m.%Y %H:%M"))

    log_text = (
        f"📦 *Новый заказ канцелярии*\n"
        f"*Пользователь:* {user_info}\n"
        f"*Тип заказа:* {'Срочный' if order_type == ORDER_URGENT else 'Обычный'}\n"
        f"*Товары:* {items}\n\n"
        f"🕒 *Заказ подан:* {timestamp}"
    )

    if callback.data == "confirm_order":
        try:
            await callback.bot.send_message(
                CHAT_ID_GENERAL,
                log_text,
                parse_mode="MarkdownV2",
                disable_web_page_preview=True,
            )
            logger.info(f"Пользователь {user_id} подтвердил заказ канцелярии")
            await callback.message.answer(
                "✅ Заказ подтвержден и отправлен!", reply_markup=return_main_menu
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке заказа пользователя {user_id}: {e}")
            await callback.message.answer(
                f"❗ Ошибка при отправке: {e}", reply_markup=return_main_menu
            )
    else:
        logger.info(f"Пользователь {user_id} отменил заказ канцелярии")
        await callback.message.answer(
            "❌ Заказ отменён.", reply_markup=return_main_menu
        )

    await state.clear()
