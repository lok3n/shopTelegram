import os
from typing import Dict

from fastapi import FastAPI, Request, status
from main import bot
from utils.models import Users, Payments, Product
import logging

app = FastAPI()


def serialization(data_str: str) -> Dict:
    data = {}
    for i in data_str.split("&"):
        key, value = i.split("=")
        data[key] = value
    return data


@app.post("/payment")
async def root(request: Request):
    body = await request.body()
    data = serialization(body.decode("utf-8"))
    print(body.decode("utf-8"))
    logging.info(f'NEW PAYMENT - {body.decode("utf-8")}')
    admins = os.getenv('ADMINS').split(',')
    try:
        payment = Payments.get_by_id(int(data.get("label")))
    except Exception as e:
        for admin in admins:
            await bot.send_message(int(admin),
                                   f'❌ Пришел неопознанный платеж под номером #{data.get("label")}\n'
                                   f'Сумма: {data.get("amount")}₽\n'
                                   f'Сумма списания: {data.get("withdraw_amount")}₽\n'
                                   f'error: {e}')
        return status.HTTP_402_PAYMENT_REQUIRED
    if float(payment.amount) != float(data.get('withdraw_amount')):
        for admin in admins:
            await bot.send_message(int(admin),
                                   f'❌ Пришел опознанный платеж под номером #{data.get("label")} с другой суммой\n'
                                   f'Сумма: {data.get("amount")}₽\n'
                                   f'Сумма списания: {data.get("withdraw_amount")}₽\n'
                                   f'Сумма в платеже: {payment.amount}₽')
        return status.HTTP_402_PAYMENT_REQUIRED
    if payment.finished == 0:
        payment.finished = 1
        payment.save()
        user = Users.get_or_none(Users.user_id == payment.user_id)
        await bot.edit_message_text(text='✅ Платёж успешно выполнен!',
                                    chat_id=payment.user_id,
                                    message_id=payment.message_id)
        for admin in admins:
            await bot.send_message(int(admin), f'''🆕 Поступил новый платёж 🆕\n
💼 Имя кошелька, куда пришел платёж: {payment.used_token.name}
🆔 Номер платежа: {payment.id}
👤 Пользователь: {user.name}
🪪 Логин: {user.username}
💰 Сумма: {payment.amount}₽ [{data.get("withdraw_amount")}₽]''')
        for product_id in payment.products.split(','):
            try:
                product = Product.get_by_id(int(product_id))
                await bot.send_photo(payment.user_id, product.photo_id, caption=f'{product.description}')
                product.delete_instance()
            except:
                for admin in admins:
                    await bot.send_message(int(admin),
                                           f'❌ Ошибка при выдаче товара пользователю по платежу {payment.id}\n'
                                           f'Скорее всего, товар был выкуплен другим человеком')
    else:
        for admin in admins:
            await bot.send_message(int(admin), f'❌ Платёж #{data.get("label")} уже был обработан')
    return status.HTTP_200_OK
