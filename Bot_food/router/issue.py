from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

# Клавиатура с выбором типа проблемы
problem_type_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Поломка", callback_data="problem_breakdown"),
            InlineKeyboardButton(text="Подменная техника", callback_data="problem_replacement"),
        ]
    ]
)

# Состояния
class ProblemRequest(StatesGroup):
    problem_type = State()
    problem_description = State()


# Обработка команды "Сообщить о проблеме/поломке"
@router.message(lambda message: message.text.lower() == "сообщить о проблеме")
async def problem_request(message: types.Message, state: FSMContext):
    await state.set_state(ProblemRequest.problem_type)
    await message.answer(
        "Пожалуйста, выберите тип проблемы:",
        reply_markup=problem_type_keyboard
    )


# Обработка выбора типа проблемы
@router.callback_query(lambda c: c.data in ["problem_breakdown", "problem_replacement"])
async def handle_problem_type(callback: CallbackQuery, state: FSMContext):
    # Сохраняем тип проблемы
    await state.update_data(problem_type=callback.data)

    await callback.message.edit_text(
        "Пожалуйста, опишите ситуацию:"
    )
    await state.set_state(ProblemRequest.problem_description)
    await callback.answer()


# Обработка описания проблемы
@router.message(ProblemRequest.problem_description)
async def handle_problem_description(message: types.Message, state: FSMContext):
    # Сохраняем описание проблемы
    await state.update_data(problem_description=message.text)

    # Получаем все данные
    data = await state.get_data()

    # Формируем итоговое сообщение
    problem_type = "Поломка" if data['problem_type'] == "problem_breakdown" else "Подменная техника"
    description = data['problem_description']

    # Подтверждение, что заявка отправлена
    await message.answer(
        f"Спасибо, ваша заявка отправлена!\n\nТип проблемы: {problem_type}\nОписание: {description}\nХорошего дня!"
    )

    # Очищаем состояние
    await state.clear()
