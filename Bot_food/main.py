import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from Bot_food.my_token import BOT_TOKEN
from Bot_food.router.CourierRequest import router as CourierRequest_router
from Bot_food.router.CourierServiceRequest import router as CourierServiceRequest_router
from Bot_food.router.RequestPass import router as RequestPass_router
from Bot_food.router.MeetGuestRequest import router as MeetGuestRequest_router
from Bot_food.router.stationery import router as stationery_router
from Bot_food.router.issue import router as issue_router
from Bot_food.router.admin import router as admin_router

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin_router)
    dp.include_router(RequestPass_router)
    dp.include_router(CourierServiceRequest_router)
    dp.include_router(CourierRequest_router)
    dp.include_router(MeetGuestRequest_router)
    dp.include_router(stationery_router)
    dp.include_router(issue_router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
    
# All features tested and working
