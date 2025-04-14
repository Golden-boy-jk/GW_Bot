from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram import Router, types

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

confirm_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", callback_data="confirm_request"
            ),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_request"),
        ]
    ]
)


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


@router.message(lambda message: message.text == "Заявка на курьерскую службу (KSE)")
async def courier_service_request(message: types.Message, state: FSMContext):
    await state.set_state(CourierServiceRequest.service_type)
    await message.answer(
        "Выберите тип курьерской службы:", reply_markup=courier_keyboard
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


@router.callback_query(lambda c: c.data in ["confirm_request", "cancel_request"])
async def handle_confirmation(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm_request":
        data = await state.get_data()
        await callback.message.answer(
            "✅ Заявка подтверждена и отправлена!", reply_markup=main_menu
        )
    else:
        await callback.message.answer("❌ Заявка отменена.", reply_markup=main_menu)

    await state.clear()
    await callback.answer()


@router.message(CourierServiceRequest.spb_recipient)
async def process_spb_recipient(message: types.Message, state: FSMContext):
    await state.update_data(spb_recipient=message.text)
    data = await state.get_data()

    summary = (
        f"📦 Заявка на курьерскую службу\n"
        f"Тип: {data.get('service_type')}\n"
        f"Имя: {data.get('recipient_name')}\n"
        f"Адрес: {data.get('recipient_address')}\n"
        f"Телефон: {data.get('recipient_phone')}\n"
        f"Документы: {data.get('document_name')}\n"
        f"Что доставляется: {data.get('item_description')}\n"
        f"Срок: {data.get('deadline')}\n"
        f"Комментарий: {data.get('comment')}\n"
        f"Получатель в СПБ: {data.get('spb_recipient')}"
    )

    await message.answer(summary, reply_markup=confirm_keyboard, parse_mode="Markdown")
