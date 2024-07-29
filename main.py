import sys

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand
from dotenv import load_dotenv
import asyncio
import os
import logging

from utils.models import Users, Locations, Product, Settings, Tokens, Payments
from handlers import *

load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()
dp.include_routers(locations_router, start_router, info_router, ap_router, admin_info_router,
                   admin_locations_router, buy_router, adm_products_router, addYoomoney_router,
                   show_logs_router, admin_mailing_router)


async def db_init():
    tables = [Users, Settings, Locations, Product, Tokens, Payments]
    for table in tables:
        if not table.table_exists():
            table.create_table()
    Settings.get_or_create()


async def main():
    await db_init()
    print('started')
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.basicConfig(filename='logs.log', level=logging.INFO)
    await bot.set_my_commands([BotCommand(command='start', description='Главное меню')])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
