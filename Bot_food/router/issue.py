from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from Bot_food.config import CHAT_ID_GENERAL

router = Router()

# Клавиатура выбора типа проблемы
problem_type_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Поломка (заменить лампочку, починить стул и т.д.)",
                callback_data="problem_breakdown"
            )
        ],
        [
            InlineKeyboardButton(
                text="Подменная техника (наушники, мышь, зарядка и т.д.)",
                callback_data="problem_replacement"
            )
        ]
    ]
)


# Состояния
class ProblemRequest(StatesGroup):
    problem_type = State()
    problem_description = State()


# Формирование текста сообщения для админа
def format_problem_report(data: dict, user: types.User) -> str:
    problem_type = (
        "Поломка"
        if data["problem_type"] == "problem_breakdown"
        else "Подменная техника"
    )
    return (
        f"📢 Новая заявка на проблему!\n\n"
        f"Тип проблемы: {problem_type}\n"
        f"Описание: {data['problem_description']}\n\n"
        f"Пользователь: @{user.username or 'не указан'}\n"
        f"User ID: {user.id}"
    )


# Команда: Сообщить о проблеме
@router.message(lambda msg: msg.text and msg.text.lower() == "сообщить о проблеме")
async def problem_request(message: types.Message, state: FSMContext):
    await state.set_state(ProblemRequest.problem_type)
    await message.answer(
        "Пожалуйста, выберите тип проблемы:", reply_markup=problem_type_keyboard
    )


# Выбор типа проблемы
@router.callback_query(lambda c: c.data in ["problem_breakdown", "problem_replacement"])
async def handle_problem_type(callback: CallbackQuery, state: FSMContext):
    await state.update_data(problem_type=callback.data)
    await callback.message.edit_text("Пожалуйста, опишите ситуацию:")
    await state.set_state(ProblemRequest.problem_description)
    await callback.answer()


# Ввод описания проблемы
@router.message(ProblemRequest.problem_description)
async def handle_problem_description(message: types.Message, state: FSMContext):
    await state.update_data(problem_description=message.text)
    data = await state.get_data()

    # Отправка админу
    try:
        await message.bot.send_message(
            CHAT_ID_GENERAL, format_problem_report(data, message.from_user)
        )
    except Exception as e:
        print(f"Ошибка при отправке админу: {e}")

    # Ответ пользователю
    problem_type = (
        "Поломка"
        if data["problem_type"] == "problem_breakdown"
        else "Подменная техника"
    )
    await message.answer(
        f"Спасибо, ваша заявка отправлена!\n\n"
        f"Тип проблемы: {problem_type}\n"
        f"Описание: {data['problem_description']}\n"
        f"Хорошего дня! 🌞"
    )

    await state.clear()
