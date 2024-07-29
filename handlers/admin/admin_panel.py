from datetime import date
from aiogram import F, Router
from aiogram.types import CallbackQuery
from utils.models import Users, Locations, Product
from utils.keyboards import admin_panel_kb
from filters.admin import IsAdmin
from aiogram.fsm.context import FSMContext


ap_router = Router()


@ap_router.callback_query(IsAdmin(), F.data == 'admin_panel')
async def admin_panel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('⏳ Загрузка . . .')
    await callback.message.edit_text(f'''🛡️ Вы перешли в административную панель для управления ботом
👥 Пользователей зарегистрировано: <b>{len([i for i in Users.select()])} человек</b>
📅 Зарегистрировано сегодня: <b>{len([i for i in Users.select(Users.registration_date == date.today())])} человек</b>
📍 Локаций создано: <b>{len([i for i in Locations.select()])} шт</b>
📦 Товаров выставлено: <b>{len([i for i in Product.select()])} шт</b>''',
                                     reply_markup=admin_panel_kb(), parse_mode='HTML')
