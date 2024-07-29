from aiogram import F, Router
from filters.admin import IsAdmin
from aiogram.types import CallbackQuery, FSInputFile

show_logs_router = Router()


@show_logs_router.callback_query(IsAdmin(), F.data == 'show_logs')
async def show_logs_handler(callback: CallbackQuery):
    await callback.message.answer_document(FSInputFile('logs.log'))
