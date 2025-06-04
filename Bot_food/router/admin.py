from aiogram import Router, types, F
from aiogram.types import Message
from Bot_food.config import ADMINS
from Bot_food.router.users.users_db import users_db, save_users
from Bot_food.router.keyboards import main_menu, admin_menu
from aiogram.fsm.context import FSMContext
import logging


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # Очищаем состояние пользователя перед стартом

    user_id = message.from_user.id
    username = message.from_user.username
    username_display = f"@{username}" if username else "пользователь без username"

    if user_id not in users_db:
        users_db.add(user_id)
        save_users(users_db)
        logger.info(
            f"✅ Новый пользователь зарегистрирован: {user_id} ({username_display})"
        )
    else:
        logger.info(
            f"📌 Уже зарегистрированный пользователь: {user_id} ({username_display})"
        )

    greeting = f"👋 Привет, {username_display}! Выберите действие:"
    await message.answer(greeting, reply_markup=main_menu)


def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


@router.message(F.text == "/admin")
async def admin_only(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(
            "🚫 У тебя нет доступа к этой команде.", reply_markup=main_menu
        )
        return
    await message.answer(
        f"👑 Привет, админ {message.from_user.full_name}!", reply_markup=admin_menu
    )


@router.message(F.text == "/logout")
async def admin_logout(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Ты и так не в админ-панели.", reply_markup=main_menu)
        return
    await message.answer(
        "✅ Ты вышел из админ-панели. Чтобы снова войти, используй /admin.",
        reply_markup=main_menu,
    )


@router.message(F.text == "/stats")
async def cmd_stats(message: Message):
    if message.from_user.id not in ADMINS:
        return
    await message.answer(f"📊 Всего пользователей в базе: {len(users_db)}")


# Фоновая отправка сообщения
async def send_broadcast(bot, user_id: int, text: str) -> bool:
    try:
        await bot.send_message(user_id, text)
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки пользователю {user_id}: {e}")
        return False


@router.message(F.text.startswith("/broadcast"))
async def cmd_broadcast(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer(
            "🚫 У вас нет доступа к этой команде.", reply_markup=main_menu
        )
        return

    text = message.text[len("/broadcast") :].strip()
    if not text:
        await message.answer(
            "❗ Укажите текст после команды /broadcast", reply_markup=admin_menu
        )
        return

    sent = 0
    for user_id in users_db:
        try:
            await message.bot.send_message(user_id, text)
            sent += 1
        except Exception as e:
            print(f"Ошибка при отправке {user_id}: {e}")

    await message.answer(
        f"✅ Сообщение отправлено {sent} пользователям.", reply_markup=admin_menu
    )
