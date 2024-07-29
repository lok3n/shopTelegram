from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from utils.keyboards import back_btn, submit_kb
from aiogram.fsm.context import FSMContext
from utils.states import Admin
from filters.admin import IsAdmin
from utils.models import Users
from aiogram.exceptions import TelegramBadRequest

admin_mailing_router = Router()


@admin_mailing_router.callback_query(IsAdmin(), F.data == 'admin_maling')
async def admin_mailing_handle(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('ℹ️ Введите текст, который хотите отправить по всей базе пользователей',
                                     reply_markup=back_btn('admin_panel'))
    await state.set_state(Admin.input_text_mailing)
    await state.update_data(past_msg_id=callback.message.message_id)


@admin_mailing_router.message(IsAdmin(), Admin.input_text_mailing)
async def input_text_mailing(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    await state.clear()
    await message.bot.edit_message_text(message.text,
                                        chat_id=message.from_user.id,
                                        message_id=data['past_msg_id'],
                                        reply_markup=submit_kb('submit_admin_mail', 'admin_panel'))


@admin_mailing_router.callback_query(IsAdmin(), F.data == 'submit_admin_mail')
async def submit_admin_mail_handle(callback: CallbackQuery):
    users = Users.select()
    sending_text = callback.message.text
    await callback.message.edit_text('⏳ В процессе . . .')
    for user in users:
        try:
            await callback.bot.send_message(user.user_id, sending_text)
        except TelegramBadRequest:
            user.delete_instance()
    await callback.message.edit_text('✅ Успешно!', reply_markup=back_btn('admin_panel'))
