from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.models import Settings
from utils.keyboards import admin_info_kb, back_btn
from filters.admin import IsAdmin
from utils.states import Admin

admin_info_router = Router()


@admin_info_router.callback_query(IsAdmin(), F.data == 'admin_info')
async def admin_info_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    settings = Settings.get()
    await callback.message.edit_text(f'📌 Ниже показан текст, который сейчас находится в разделе «Информация»\n'
                                     f'✍️ Чтобы отредактировать этот текст, нажмите на кнопку «Редактировать»\n\n'
                                     f'{settings.info_text}',
                                     reply_markup=admin_info_kb('admin_info_edit'))


@admin_info_router.callback_query(IsAdmin(), F.data == 'admin_info_edit')
async def admin_info_edit_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('✍️ Введите новый текст для раздела «Информация»',
                                     reply_markup=back_btn('admin_info'))
    await state.update_data(past_msg_id=callback.message.message_id)
    await state.set_state(Admin.edit_info_text)


@admin_info_router.message(IsAdmin(), Admin.edit_info_text)
async def admin_info_editing_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    await message.bot.edit_message_text('⏳ Загрузка . . .', chat_id=message.from_user.id,
                                        message_id=int(data['past_msg_id']))
    settings = Settings.get()
    settings.info_text = message.text
    settings.save()
    await state.clear()
    await message.bot.edit_message_text(f'✅ Вы успешно поменяли текст, теперь он такой:\n\n{message.text}',
                                        chat_id=message.from_user.id,
                                        message_id=int(data['past_msg_id']),
                                        reply_markup=back_btn('admin_panel'))


@admin_info_router.callback_query(IsAdmin(), F.data == 'admin_help_pay')
async def admin_help_pay_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    settings = Settings.get()
    await callback.message.edit_text(f'📌 Ниже показан текст, который сейчас находится в разделе «Оплата»\n'
                                     f'✍️ Чтобы отредактировать этот текст, нажмите на кнопку «Редактировать»\n\n'
                                     f'{settings.pay_text}',
                                     reply_markup=admin_info_kb('admin_help_pay_edit'))


@admin_info_router.callback_query(IsAdmin(), F.data == 'admin_help_pay_edit')
async def admin_info_edit_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('✍️ Введите новый текст для раздела «Оплата»',
                                     reply_markup=back_btn('admin_help_pay'))
    await state.update_data(past_msg_id=callback.message.message_id)
    await state.set_state(Admin.edit_pay_text)


@admin_info_router.message(IsAdmin(), Admin.edit_pay_text)
async def admin_info_editing_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    await message.bot.edit_message_text('⏳ Загрузка . . .', chat_id=message.from_user.id,
                                        message_id=int(data['past_msg_id']))
    settings = Settings.get()
    settings.pay_text = message.text
    settings.save()
    await state.clear()
    await message.bot.edit_message_text(f'✅ Вы успешно поменяли текст, теперь он такой:\n\n{message.text}',
                                        chat_id=message.from_user.id,
                                        message_id=int(data['past_msg_id']),
                                        reply_markup=back_btn('admin_panel'))
