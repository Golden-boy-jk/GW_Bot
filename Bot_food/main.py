from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging
from my_token import TOKEN
from router.CourierRequest import router as CourierRequest_router
from router.CourierServiceRequest import router as CourierServiceRequest_router
from router.RequestPass import router as RequestPass_router
from router.MeetGuestRequest import router as MeetGuestRequest_router

# Настрой логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Подключаем каждый роутер по очереди
dp.include_router(RequestPass_router)
dp.include_router(CourierServiceRequest_router)
dp.include_router(CourierRequest_router)
dp.include_router(MeetGuestRequest_router)


# Запускаем бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
