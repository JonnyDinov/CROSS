from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from medieval_bot.database.models import User
from medieval_bot.database.engine import async_session_maker
from medieval_bot.keyboards.inline import shop_menu_keyboard
from medieval_bot.utils.currency import format_currency
from medieval_bot.constants import SHOP_ITEMS, SHOP_CATEGORIES

router = Router()

@router.callback_query(F.data.startswith("shop_"))
async def show_shop_category(callback: CallbackQuery):
    """Отображение категории товаров"""
    category = callback.data.replace("shop_", "")
    
    items = SHOP_ITEMS.get(category, [])
    
    items_text = ""
    for item in items:
        items_text += f"\n• <b>{item['name']}</b>\n"
        items_text += f"  {item['description']}\n"
        items_text += f"  Цена: {format_currency(item['price'])}\n"
    
    shop_text = f"""<b>{SHOP_CATEGORIES.get(category, 'Магазин')}</b>
━━━━━━━━━━━━━━━━━━━━

{items_text}

<i>Система покупок будет доступна в следующих обновлениях.
Пока ты можешь просматривать ассортимент.</i>"""
    
    await callback.message.edit_text(
        shop_text,
        reply_markup=shop_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
