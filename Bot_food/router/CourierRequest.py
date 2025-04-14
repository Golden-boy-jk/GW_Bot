from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

router = Router()

# Клавиатура подтверждения
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


# Состояния
class CourierRequest(StatesGroup):
    from_address = State()
    sender_info = State()
    to_address = State()
    recipient_info = State()
    item_description = State()
    deadline = State()
    comment = State()
    attachment = State()


# Обработка начала заявки
@router.message(lambda message: message.text == "Заявка на офисного курьера")
async def courier_request(message: types.Message, state: FSMContext):
    await state.set_state(CourierRequest.from_address)
    await message.answer(
        "Заявки оформляются за 1 день и более, доставка по СПБ и ближайшей области.\n"
        "Адрес (откуда):"
    )


@router.message(CourierRequest.from_address)
async def process_from_address(message: types.Message, state: FSMContext):
    await state.update_data(from_address=message.text)
    await state.set_state(CourierRequest.sender_info)
    await message.answer("Введите данные отправителя:")


@router.message(CourierRequest.sender_info)
async def process_sender_info(message: types.Message, state: FSMContext):
    await state.update_data(sender_info=message.text)
    await state.set_state(CourierRequest.to_address)
    await message.answer("Введите адрес (куда доставить):")


@router.message(CourierRequest.to_address)
async def process_to_address(message: types.Message, state: FSMContext):
    await state.update_data(to_address=message.text)
    await state.set_state(CourierRequest.recipient_info)
    await message.answer("Введите данные получателя:")


@router.message(CourierRequest.recipient_info)
async def process_recipient_info(message: types.Message, state: FSMContext):
    await state.update_data(recipient_info=message.text)
    await state.set_state(CourierRequest.item_description)
    await message.answer("Что доставляем? Опишите:")


@router.message(CourierRequest.item_description)
async def process_item_description(message: types.Message, state: FSMContext):
    await state.update_data(item_description=message.text)
    await state.set_state(CourierRequest.deadline)
    await message.answer("Крайний срок доставки:")


@router.message(CourierRequest.deadline)
async def process_deadline(message: types.Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await state.set_state(CourierRequest.comment)
    await message.answer("Комментарий (если есть):")


@router.message(CourierRequest.comment)
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(CourierRequest.attachment)
    await message.answer(
        "Хотите приложить изображение или документ?\n"
        "📎 Просто отправьте файл или нажмите 'Пропустить'",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Пропустить", callback_data="skip_attachment"
                    )
                ]
            ]
        ),
    )


@router.message(CourierRequest.attachment)
async def process_attachment(message: types.Message, state: FSMContext):
    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer("Пожалуйста, отправьте изображение или документ.")
        return

    await state.update_data(attachment=file_id)
    await show_summary(message, state)


@router.callback_query(lambda c: c.data == "skip_attachment")
async def skip_attachment(callback: CallbackQuery, state: FSMContext):
    await state.update_data(attachment=None)
    await callback.answer()
    await show_summary(callback.message, state)


# Подтверждение / отмена
@router.callback_query(lambda c: c.data in ["confirm_request", "cancel_request"])
async def handle_confirmation(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm_request":
        data = await state.get_data()
        await callback.message.answer("✅ Заявка подтверждена и отправлена!")
        # Здесь можно отправить админу
        # await bot.send_message(ADMIN_ID, форматированный_текст)
    else:
        await callback.message.answer("❌ Заявка отменена.")

    await state.clear()
    await callback.answer()


# Финальный вывод заявки
async def show_summary(message: types.Message, state: FSMContext):
    data = await state.get_data()

    summary = (
        "📦 **Заявка на офисного курьера**\n"
        f"**Откуда:** {data['from_address']}\n"
        f"**Отправитель:** {data['sender_info']}\n"
        f"**Куда:** {data['to_address']}\n"
        f"**Получатель:** {data['recipient_info']}\n"
        f"**Что доставить:** {data['item_description']}\n"
        f"**Срок:** {data['deadline']}\n"
        f"**Комментарий:** {data['comment'] or '-'}"
    )

    await message.answer(summary, parse_mode="Markdown")

    if data.get("attachment"):
        # Отправляем файл, если он есть
        try:
            await message.answer_document(data["attachment"])
        except Exception:
            await message.answer("⚠️ Не удалось отправить вложение.")

    await message.answer("Подтвердите заявку:", reply_markup=confirm_keyboard)
