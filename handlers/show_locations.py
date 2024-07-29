from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from utils.keyboards import locations_kb, products_counter
from utils.models import Locations, Product

locations_router = Router()


@locations_router.callback_query(F.data == 'show_locations')
async def show_locations_handler(callback: CallbackQuery):
    await callback.message.edit_text('📌 Теперь выбери локацию, где хочешь забрать свой товар',
                                     reply_markup=locations_kb(Locations.select()))


@locations_router.callback_query(F.data.startswith('show_loc'))
async def show_loc_handler(callback: CallbackQuery, state: FSMContext):
    location = Locations.get_by_id(int(callback.data.split()[1]))
    products = [i for i in Product.select().where(Product.location == location.id)]
    if not products:
        return await callback.answer('❌ В этой локации кончились товары')
    await state.update_data(value=1, max_value=len(products), location=location.id)
    await callback.message.edit_text(f'📍 Вы выбрали локацию {location.name}\n'
                                     f'🔢 Выберите кол-во товара и нажмите «Купить»',
                                     reply_markup=products_counter(1, False, len(products) > 1, location))


@locations_router.callback_query(F.data.startswith('view'))
async def view_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    do = callback.data.split()[1]
    value, max_value = int(data['value']), int(data['max_value'])
    location = Locations.get_by_id(int(data['location']))
    add, sub = True, True
    if do == 'add' and value + 1 == max_value:
        add = False
    elif do == 'sub' and value - 1 == 1:
        sub = False
    try:
        if do == 'add':
            await callback.message.edit_reply_markup(reply_markup=products_counter(value + 1, sub, add, location))
            await state.update_data(value=value + 1)
        elif do == 'sub':
            await callback.message.edit_reply_markup(reply_markup=products_counter(value - 1, sub, add, location))
            await state.update_data(value=value - 1)
    except TelegramBadRequest:
        pass
