# from aiogram import Router, F, types
# from aiogram.fsm.context import FSMContext
# import logging
# from aiogram.types import Message
# from Bot_food.router.users.users_db import users_db
# from Bot_food.router.keyboards import main_menu
#
# router = Router()
# logger = logging.getLogger(__name__)
#
#
# @router.message(F.text == "/start")
# async def cmd_start(message: types.Message, state: FSMContext):
#     await state.clear()  # Очищаем состояние пользователя перед стартом
#
#     user_id = message.from_user.id
#     username = message.from_user.username
#     username_display = f"@{username}" if username else "пользователь без username"
#
#     if user_id not in users_db:
#         users_db.add(user_id)
#         logger.info(f"✅ Новый пользователь зарегистрирован: {user_id} ({username_display})")
#     else:
#         logger.info(f"📌 Уже зарегистрированный пользователь: {user_id} ({username_display})")
#
#     greeting = f"👋 Привет, {username_display}! Выберите действие:"
#     await message.answer(greeting, reply_markup=main_menu)
#
#
# @router.message(F.text == "/check_users")
# async def check(message: Message):
#     await message.answer(f"📊 Зарегистрировано пользователей: {len(users_db)}")
#
#
# @router.message()
# async def default_handler(message: Message):
#     logger.info(f"⚠️ Необработанное сообщение от {message.from_user.id}: {message.text}")
#     await message.answer("🤖 Я не понимаю это сообщение. Пожалуйста, выбери действие из меню.")
