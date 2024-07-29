from aiogram import F, Router
from aiogram.types import CallbackQuery
from utils.models import Settings
from utils.keyboards import back_btn

info_router = Router()


@info_router.callback_query(F.data == 'show_info')
async def show_info_handler(callback: CallbackQuery):
    settings = Settings.get()
    await callback.message.edit_text(settings.info_text, reply_markup=back_btn('start'))
