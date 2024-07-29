from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from filters.admin import IsAdmin
from utils.keyboards import admin_locations_kb, back_btn, admin_show_loc_kb, cancel_btn, adm_submit_and_cancel
from utils.models import Locations, Product
from utils.states import Admin

admin_locations_router = Router()


@admin_locations_router.callback_query(IsAdmin(), F.data == 'admin_locations')
async def admin_locations_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('🛡️ Ниже весь список локаций, чтобы добавить новую локацию нажмите '
                                     '«Добавить локацию»\n'
                                     'Если Вы хотите удалить какую-то локацию, выберите её и нажмите «Удалить локацию»'
                                     ', при это все товары из этой локации тоже удалятся',
                                     reply_markup=admin_locations_kb(Locations.select()))


@admin_locations_router.callback_query(IsAdmin(), F.data == 'add_location')
async def add_location_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('➕ Введите название новой локации, чтобы вернуться к списку локаций нажмите '
                                     'на кнопку «Назад»',
                                     reply_markup=back_btn('admin_locations'))
    await state.update_data(past_msg_id=callback.message.message_id)
    await state.set_state(Admin.add_location)


@admin_locations_router.message(IsAdmin(), Admin.add_location)
async def add_location_input_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    location = Locations.get_or_none(Locations.name == message.text)
    if location:
        return await message.bot.edit_message_text(
            '❌ Такая локация уже существует\n➕ Введите название новой локации, чтобы вернуться к списку локаций '
            'нажмите на кнопку «Назад»', chat_id=message.from_user.id, message_id=int(data['past_msg_id']))
    await message.bot.edit_message_text('⏳ Загрузка . . .', chat_id=message.from_user.id,
                                        message_id=int(data['past_msg_id']))
    location = Locations.create(name=message.text)
    await state.clear()
    await message.bot.edit_message_text(f'✅ Вы успешно создали новую локацию с названием:\n\n{message.text}',
                                        chat_id=message.from_user.id,
                                        message_id=int(data['past_msg_id']),
                                        reply_markup=back_btn('admin_locations'))


@admin_locations_router.callback_query(IsAdmin(), F.data.startswith('adm_show_loc'))
async def adm_show_loc_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    products = Product.select().where(Product.location == int(callback.data.split()[1]))
    location = Locations.get_by_id(int(callback.data.split()[1]))
    await callback.message.edit_text(f'📍 Вы выбрали локацию {location.name}\n'
                                     f'📦 Всего товаров в этой локации: {len(products)} шт',
                                     reply_markup=admin_show_loc_kb(location.id, products))


@admin_locations_router.callback_query(IsAdmin(), F.data.startswith('from_prod_adm_show_loc'))
async def adm_show_loc_handler(callback: CallbackQuery, state: FSMContext):
    '''function as upper, but this func for returning from adm_show_prod'''
    await state.clear()
    products = Product.select().where(Product.location == int(callback.data.split()[1]))
    location = Locations.get_by_id(int(callback.data.split()[1]))
    await callback.message.delete()
    await callback.message.answer(f'📍 Вы выбрали локацию {location.name}\n'
                                  f'📦 Всего товаров в этой локации: {len(products)} шт',
                                  reply_markup=admin_show_loc_kb(location.id, products))


@admin_locations_router.callback_query(IsAdmin(), F.data.startswith('delete_location'))
async def delete_location_handler(callback: CallbackQuery):
    try:
        products = Product.select().where(Product.location == int(callback.data.split()[1]))
        for i in products:
            i.delete_instance()
        location = Locations.get_by_id(int(callback.data.split()[1]))
        location.delete_instance()
        await callback.message.edit_text(f'✅ Вы успешно удалили локацию {location.name}\n'
                                         f'📦 Всего товаров удалено, которые были в этой локации: {len(products)} шт',
                                         reply_markup=back_btn('admin_locations'))
    except Exception as e:
        await callback.message.edit_text(f'Возникла ошибка в боте: {e}\n'
                                         f'Свяжитесь с @whytek для починки бота\n'
                                         f'{callback.data}')


@admin_locations_router.callback_query(IsAdmin(), F.data.startswith('add_product'))
async def add_product_handler(callback: CallbackQuery, state: FSMContext):
    location = Locations.get_by_id(int(callback.data.split()[1]))
    await callback.message.edit_text(f'📍 Вы выбрали локацию {location.name}\n'
                                     f'🖼️ Пришлите фотографию расположения товара',
                                     reply_markup=cancel_btn(f'adm_show_loc {location.id}'))
    await state.update_data(past_msg_id=callback.message.message_id,
                            location=location.id)
    await state.set_state(Admin.input_product_photo)


@admin_locations_router.message(IsAdmin(), Admin.input_product_photo)
async def input_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    if not message.photo:
        return await message.bot.edit_message_text('❌ Ошибка! Пришлите фото расположения товара',
                                                   chat_id=message.from_user.id,
                                                   message_id=int(data['past_msg_id']),
                                                   reply_markup=cancel_btn(f'adm_show_loc {data['location']}'))
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(Admin.input_product_description)
    await message.bot.edit_message_text('✅ Вы успешно загрузили фото!\n\n'
                                        '📝 Заполните описание товара и места где он находится',
                                        chat_id=message.from_user.id,
                                        message_id=int(data['past_msg_id']),
                                        reply_markup=cancel_btn(f'adm_show_loc {data['location']}'))


@admin_locations_router.message(IsAdmin(), Admin.input_product_description)
async def input_description(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    await state.update_data(description=message.text)
    await state.set_state(Admin.input_product_price)
    await message.bot.edit_message_text(f'✅ Вы успешно установили описание: {message.text}\n\n'
                                        '💵 Введите стоимость добавляемого товара',
                                        chat_id=message.from_user.id,
                                        message_id=int(data['past_msg_id']),
                                        reply_markup=cancel_btn(f'adm_show_loc {data['location']}'))


@admin_locations_router.message(IsAdmin(), Admin.input_product_price)
async def input_price(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    if not message.text.isdigit():
        return await message.bot.edit_message_text(f'❌ Ошибка! Цена должна состоять только из цифр',
                                                   chat_id=message.from_user.id,
                                                   message_id=int(data['past_msg_id']),
                                                   reply_markup=cancel_btn(f'adm_show_loc {data['location']}'))
    await state.set_state(Admin.submit)
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=int(data['past_msg_id']))
    msg = await message.answer_photo(data['photo'], f'''👉 Проверьте все введённые Вами данные

📝 Описание: {data["description"]}
💵 Стоимость товара: {message.text} рублей''', reply_markup=adm_submit_and_cancel())
    await state.update_data(price=message.text, past_msg_id=msg.message_id)


@admin_locations_router.callback_query(IsAdmin(), F.data.startswith('new_product'))
async def submit_new_product_handle(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    location = Locations.get_by_id(int(data['location']))
    await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=int(data['past_msg_id']))
    if callback.data.split()[1] == 'submit':
        Product.create(location=location.id, photo_id=data['photo'], description=data['description'],
                       price=int(data['price']))
        await state.clear()
        await callback.message.answer(f'✅ Вы добавили новый товар в локацию {location.name}',
                                      reply_markup=back_btn(f'adm_show_loc {location.id}'))
    elif callback.data.split()[1] == 'cancel':
        await state.clear()
        await callback.message.answer(f'❌ Вы отменили добавление товара в локацию {location.name}',
                                      reply_markup=back_btn(f'adm_show_loc {location.id}'))
