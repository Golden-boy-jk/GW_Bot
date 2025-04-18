from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)


def order_type_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Срочно", callback_data="order_type_urgent"),
                InlineKeyboardButton(
                    text="Ближайшая доставка", callback_data="order_type_regular"
                ),
            ]
        ]
    )
    return keyboard


router = Router()


class OrderStationeryStates(StatesGroup):
    waiting_for_items = State()


@router.message(lambda message: message.text.lower() == "заказ канцелярии")
async def order_stationery(message: Message):
    await message.answer("Выберите тип заказа:", reply_markup=order_type_keyboard())


# Обработка кнопок выбора типа
@router.callback_query(
    lambda callback: callback.data == "order_type_urgent"
    or callback.data == "order_type_regular"
)
async def handle_order_type(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Заказ осуществляется через компанию Комус.\n"
        "Вставьте артикул или перечислите необходимые товары для заказа:"
    )
    await state.set_state(OrderStationeryStates.waiting_for_items)
    await callback.answer()


# Получение артикула/перечня товаров
@router.message(OrderStationeryStates.waiting_for_items)
async def receive_items(message: Message, state: FSMContext):
    # Тут можно сохранить message.text в базу или лог
    await message.answer("Ваш заказ принят. Хорошего дня! 😊")
    await state.clear()
