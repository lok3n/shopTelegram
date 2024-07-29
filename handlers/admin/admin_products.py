from aiogram import F, Router
from aiogram.types import CallbackQuery
from utils.models import Product
from filters.admin import IsAdmin
from utils.keyboards import admin_show_prod_kb, back_btn

adm_products_router = Router()


@adm_products_router.callback_query(IsAdmin(), F.data.startswith('adm_show_prod'))
async def adm_show_prod_handle(callback: CallbackQuery):
    product = Product.get_by_id(int(callback.data.split()[1]))
    await callback.message.delete()
    await callback.message.answer_photo(photo=product.photo_id,
                                        caption=f'💵 Цена: {product.price}₽\n\n{product.description}',
                                        reply_markup=admin_show_prod_kb(product.id, product.location))


@adm_products_router.callback_query(IsAdmin(), F.data.startswith('delete_product'))
async def delete_product_handle(callback: CallbackQuery):
    product = Product.get_by_id(int(callback.data.split()[1]))
    await callback.message.delete()
    await callback.message.answer('✅ Товар был успешно удалён!',
                                  reply_markup=back_btn(f'adm_show_loc {product.location}'))
    product.delete_instance()
