import logging
import os

from aiogram import F, Router
from aiogram.types import CallbackQuery
from utils.models import Locations, Product, Settings, Tokens, Payments
from utils.keyboards import pay_btn
from shop_yoomoney.quickpay import Quickpay

buy_router = Router()


@buy_router.callback_query(F.data.startswith('buy'))
async def buy_handler(callback: CallbackQuery):
    data = callback.data.split()  # buy location.id amount
    location, amount = Locations.get_by_id(int(data[1])), int(data[2])
    products = Product.select().where(Product.location == location.id).limit(amount)
    price = sum([product.price for product in products])
    settings = Settings.get()
    last_payment = Payments.select().order_by(Payments.id.desc()).get()
    tokens, token = Tokens.select().where(Tokens.avaliable == 1), None
    admins = os.getenv('ADMINS').split(',')
    if len(tokens) == 0:
        for admin in admins:
            await callback.bot.send_message(int(admin), f'❌ Ошибка! Пользователь {callback.from_user.username} '
                                                        f'пытался оплатить товар, но доступных API Токенов не осталось')
        return await callback.answer('❌ Ошибка! Свяжитесь с администрацией', show_alert=True)
    elif len(tokens) == 1:
        token = tokens.get()
    else:
        next_token = False
        for current_token in tokens:
            if next_token:
                token = current_token
            if last_payment.used_token == current_token:
                next_token = True
        if next_token and not token:
            token = tokens.get()
    if not token:
        for admin in admins:
            await callback.bot.send_message(int(admin), 'Ошибка при получении токена API, обратитесь к '
                                                        'разработчику')
        return
    payment = Payments.create(user_id=callback.from_user.id,
                              products=','.join([str(i.id) for i in products]),
                              amount=price,
                              used_token=token)
    quickpay = Quickpay(
        receiver=token.api[:token.api.find('.')],
        quickpay_form="button",
        targets="Маникюр",
        paymentType="AC",
        sum=price,
        label=str(payment.id), )
    try:
        response = await quickpay.get_url_to_pay()
    except Exception as e:
        for admin in admins:
            await callback.bot.send_message(int(admin), f'❌ Пользователь {callback.from_user.username} попытался '
                                                        f'оплатить товар по токену {token.name} и возникла ошибка\n'
                                                        f'Данный токен больше не доступен (проверьте логи, почему '
                                                        f'возникла ошибка)')
        logging.error(f'ERROR WHILE PAYING - {e}')
        token.avaliable = 0
        token.save()
        return callback.answer('🔄 Попробуйте ещё раз')
    await callback.message.edit_text(settings.pay_text, reply_markup=pay_btn(str(response.url)))
    payment.message_id = callback.message.message_id
    payment.save()
