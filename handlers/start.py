from datetime import date
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.models import Users, Settings
from utils.keyboards import main_menu
from utils.functions import is_admin

start_router = Router()


@start_router.message(Command('start'))
@start_router.callback_query(F.data == 'start')
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    settings = Settings.get()
    if isinstance(message, Message):
        user = Users.get_or_none(Users.user_id == message.from_user.id)
        if not user:
            Users.create(user_id=message.from_user.id, registration_date=date.today(),
                         name=message.from_user.full_name, username=message.from_user.username)
        await message.answer(settings.info_text, reply_markup=main_menu(await is_admin(message.from_user.id)))
    else:
        await message.message.edit_text(settings.info_text,
                                        reply_markup=main_menu(await is_admin(message.from_user.id)))
