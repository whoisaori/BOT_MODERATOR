import os
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot

from app.handlers import router  # Импортируем роутеры


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except:
        print('Exit')
