import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.states import AddYoomoney
from utils.keyboards import cancel_btn, go_to_url, back_btn
from filters.admin import IsAdmin
from shop_yoomoney.authorize import Authorize
from utils.models import Tokens

addYoomoney_router = Router()


@addYoomoney_router.callback_query(IsAdmin(), F.data == 'add_yoomoney')
async def add_yoomoney_handle(callback: CallbackQuery, state: FSMContext):
    tokens = 'Доступны кошельки:\n' + ', '.join([token.name for token in Tokens.select().where(Tokens.avaliable == 1)])
    await callback.message.edit_text(tokens + '\n\nℹ️ Вы начали процесс добавления кошелька <b>YooMoney</b>\n'
                                              '👉 Введите <i>название кошелька</i>:',
                                     reply_markup=cancel_btn('admin_panel'),
                                     parse_mode="HTML")
    await state.update_data(past_msg_id=callback.message.message_id)
    await state.set_state(AddYoomoney.input_name)


@addYoomoney_router.message(IsAdmin(), AddYoomoney.input_name)
async def input_name_handle(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.edit_message_text(text=f'✅ Вы ввели <i>название кошелька</i>: <code>{message.text}</code>\n'
                                             f'👉 Введите <i>Redirect URL</i>:',
                                        chat_id=message.chat.id,
                                        message_id=data['past_msg_id'],
                                        reply_markup=cancel_btn('admin_panel'),
                                        parse_mode="HTML")
    await state.update_data(name=message.text)
    await state.set_state(AddYoomoney.input_redirectUrl)


@addYoomoney_router.message(IsAdmin(), AddYoomoney.input_redirectUrl)
async def input_redirect_handle(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.edit_message_text(text=f'✅ Вы ввели <i>Redirect URL</i>: <code>{message.text}</code>\n'
                                             f'👉 Введите <i>Client ID</i>:',
                                        chat_id=message.chat.id,
                                        message_id=data['past_msg_id'],
                                        reply_markup=cancel_btn('admin_panel'),
                                        parse_mode="HTML")
    await state.update_data(redirect=message.text)
    await state.set_state(AddYoomoney.input_clientId)


@addYoomoney_router.message(IsAdmin(), AddYoomoney.input_clientId)
async def input_client_id_handle(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    await message.bot.edit_message_text(text=f'✅ Вы ввели <i>Client ID</i>: <code>{message.text}</code>\n'
                                             f'👉 Введите <i>Client Secret</i>:',
                                        chat_id=message.chat.id,
                                        message_id=data['past_msg_id'],
                                        reply_markup=cancel_btn('admin_panel'),
                                        parse_mode="HTML")
    await state.update_data(client_id=message.text)
    await state.set_state(AddYoomoney.input_clientSecret)


@addYoomoney_router.message(IsAdmin(), AddYoomoney.input_clientSecret)
async def input_client_secret_handle(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    await message.bot.edit_message_text(text=f'✅ Вы ввели <i>Client Secret</i>: <code>{message.text}</code>',
                                        chat_id=message.chat.id,
                                        message_id=data['past_msg_id'],
                                        reply_markup=cancel_btn('admin_panel'),
                                        parse_mode="HTML")
    await state.clear()
    client = Authorize(client_id=data['client_id'],
                       client_secret=message.text,
                       redirect_url=data['redirect'],
                       scope=["account-info",
                              "operation-history",
                              "operation-details",
                              "incoming-transfers",
                              "payment-p2p",
                              "payment-shop", ])
    response = await client.get_auth_url()
    if response.ok:
        logging.info(f'AUTH YOOMONEY FOR URL - {str(response.url)}')
        msg = await message.answer('ℹ️ Перейдите по ссылке, предоставьте права для использования кошелька, '
                                   'потом скопируйте ссылку/код из ссылки на которую Вас перенаправит и отправьте сюда',
                                   reply_markup=go_to_url(str(response.url)))
        await state.set_state(AddYoomoney.input_code)
        await state.update_data(past_msg_id=msg.message_id,
                                client=client)
    else:
        await message.answer('❌ Возникла ошибка! Код ошибки #100, просмотрите логи или обратитесь к '
                             'разработчику')
        logging.error(response.json())
        return


@addYoomoney_router.message(IsAdmin(), AddYoomoney.input_code)
async def input_code_handler(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    client = data['client']
    try:
        token = await client.input_code(message.text)
        logging.info(f'NEW TOKEN ADDED - {token}')
        Tokens.create(name=data['name'], api=token)
        await message.bot.edit_message_text(text=f'✅ Кошелёк успешно добавлен! Токен: <code>{token}</code>',
                                            chat_id=message.chat.id,
                                            message_id=data['past_msg_id'],
                                            reply_markup=back_btn('admin_panel'),
                                            parse_mode="HTML")
        await state.clear()
    except Exception as e:
        await message.bot.edit_message_text(text='❌ Ошибка при получении токена, посмотрите логи или обратитесь к '
                                                 'разработчику',
                                            chat_id=message.chat.id,
                                            message_id=data['past_msg_id'],
                                            reply_markup=back_btn('admin_panel'))
        logging.error(f'ERROR WHILE GETTING TOKEN YOOMONEY - {e}')
        print(f'ERROR WHILE GETTING TOKEN YOOMONEY - {e}')
