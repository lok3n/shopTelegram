from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from utils.models import Locations, Product


def main_menu(is_admin=False):
    builder = InlineKeyboardBuilder()
    builder.button(text='📍 Локации', callback_data='show_locations')
    # builder.button(text='ℹ️ Информация', callback_data='show_info')
    builder.button(text='🛠️ Поддержка', url='tg://user?id=5885130516')
    if is_admin:
        builder.button(text='👑 Админ-панель', callback_data='admin_panel')
    return builder.adjust(2).as_markup()


def locations_kb(locations: list[Locations]):
    builder = InlineKeyboardBuilder()
    for location in locations:
        builder.row(InlineKeyboardButton(text=location.name, callback_data=f'show_loc {location.id}'))
    builder.row(InlineKeyboardButton(text='↩️ Назад', callback_data='start'))
    return builder.as_markup()


def admin_locations_kb(locations: list[Locations]):
    builder = InlineKeyboardBuilder()
    for location in locations:
        builder.row(InlineKeyboardButton(text=location.name, callback_data=f'adm_show_loc {location.id}'))
    builder.row(InlineKeyboardButton(text='➕ Добавить локацию', callback_data='add_location'),
                InlineKeyboardButton(text='↩️ Назад', callback_data='admin_panel'))
    return builder.as_markup()


def admin_panel_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='📍 Локации', callback_data='admin_locations')
    builder.button(text='ℹ️ Информация', callback_data='admin_info')
    builder.button(text='❓ Оплата', callback_data='admin_help_pay')
    builder.button(text='🟣 ЮМани', callback_data='add_yoomoney')
    builder.button(text='🧾 Логи', callback_data='show_logs')
    builder.button(text='📩 Рассылка', callback_data='admin_maling')
    builder.button(text='↩️ Назад', callback_data='start')
    return builder.adjust(2).as_markup()


def admin_info_kb(callback):
    builder = InlineKeyboardBuilder()
    builder.button(text='✍️ Редактировать', callback_data=callback)
    builder.button(text='↩️ Назад', callback_data='admin_panel')
    return builder.adjust(1).as_markup()


def admin_show_loc_kb(location_id: int, products: list[Product]):
    builder = InlineKeyboardBuilder()
    for i, product in enumerate(products):
        builder.row(InlineKeyboardButton(text=f'📦 Товар №{i + 1}', callback_data=f'adm_show_prod {product.id}'))
    builder.row(InlineKeyboardButton(text='🗑️ Удалить локацию', callback_data=f'delete_location {location_id}'),
                InlineKeyboardButton(text='➕ Добавить товар', callback_data=f'add_product {location_id}'))
    builder.row(InlineKeyboardButton(text='↩️ Назад', callback_data=f'admin_locations'))
    return builder.as_markup()


def back_btn(callback):
    return InlineKeyboardBuilder().button(text='↩️ Назад', callback_data=callback).as_markup()


def adm_submit_and_cancel():
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Подтвердить', callback_data='new_product submit')
    builder.button(text='❌ Отменить', callback_data='new_product cancel')
    return builder.adjust(2).as_markup()


def admin_show_prod_kb(product_id: int, location_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text='🗑️ Удалить товар', callback_data=f'delete_product {product_id}')
    builder.button(text='↩️ Назад', callback_data=f'from_prod_adm_show_loc {location_id}')
    return builder.as_markup()


def products_counter(value: int, sub: bool, add: bool, location: Locations):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='💳 Купить', callback_data=f'buy {location.id} {value}'))
    buttons = []
    if sub:
        buttons.append(InlineKeyboardButton(text='◀️', callback_data='view sub'))
    buttons.append(InlineKeyboardButton(text=f'{str(value)} шт.', callback_data='none'))
    if add:
        buttons.append(InlineKeyboardButton(text='▶️', callback_data='view add'))
    builder.row(*buttons)
    builder.row(InlineKeyboardButton(text='↩️ Назад', callback_data='show_locations'))
    return builder.as_markup()


def cancel_btn(callback):
    return InlineKeyboardBuilder().button(text='❌ Отменить', callback_data=callback).as_markup()


def go_to_url(url):
    return InlineKeyboardBuilder().button(text='🌐 Перейти', url=url).as_markup()


def pay_btn(url):
    return InlineKeyboardBuilder().button(text='💳 Купить', url=url).as_markup()


def submit_kb(submit, cancel):
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Подтвердить', callback_data=submit)
    builder.button(text='❌ Отменить', callback_data=cancel)
    return builder.adjust(2).as_markup()
