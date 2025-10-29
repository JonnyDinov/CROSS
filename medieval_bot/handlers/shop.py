from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from medieval_bot.database.models import User
from medieval_bot.database.engine import async_session_maker
from medieval_bot.keyboards.inline import shop_menu_keyboard, main_menu_keyboard
from medieval_bot.utils.currency import format_currency

router = Router()

SHOP_ITEMS = {
    'weapons': [
        {'name': 'Железный меч', 'price': 5000, 'description': 'Надёжный меч для начинающего воина'},
        {'name': 'Стальной топор', 'price': 7500, 'description': 'Тяжёлый топор дварфийской работы'},
        {'name': 'Эльфийский лук', 'price': 10000, 'description': 'Изящный лук из Сильвании'},
    ],
    'armor': [
        {'name': 'Кожаные доспехи', 'price': 20000, 'description': 'Лёгкая защитная экипировка'},
        {'name': 'Кольчуга', 'price': 50000, 'description': 'Надёжная защита от мечей'},
        {'name': 'Латный доспех', 'price': 100000, 'description': 'Тяжёлая броня рыцаря'},
    ],
    'potions': [
        {'name': 'Зелье здоровья', 'price': 500, 'description': 'Восстанавливает 50 HP'},
        {'name': 'Зелье маны', 'price': 500, 'description': 'Восстанавливает 50 MP'},
        {'name': 'Зелье энергии', 'price': 300, 'description': 'Восстанавливает 50 энергии'},
    ],
    'magic': [
        {'name': 'Свиток огня', 'price': 15000, 'description': 'Позволяет сотворить огненный шар'},
        {'name': 'Свиток льда', 'price': 15000, 'description': 'Позволяет сотворить ледяную стрелу'},
        {'name': 'Свиток исцеления', 'price': 20000, 'description': 'Мощное лечебное заклинание'},
    ],
    'food': [
        {'name': 'Хлеб', 'price': 50, 'description': 'Простая еда'},
        {'name': 'Жареное мясо', 'price': 200, 'description': 'Сытная еда'},
        {'name': 'Праздничный пир', 'price': 1000, 'description': 'Роскошная трапеза'},
    ]
}

@router.callback_query(F.data == "shop")
async def show_shop_menu(callback: CallbackQuery):
    """Отображение меню магазинов"""
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.answer("Ошибка: персонаж не найден!", show_alert=True)
            return
    
    shop_text = f"""🏪 <b>Торговая улица</b>
━━━━━━━━━━━━━━━━━━━━

Твой кошелёк:
💰 {format_currency(user.copper_coins)}

Добро пожаловать на торговую улицу!
Здесь ты можешь приобрести всё необходимое для приключений.

Выбери категорию товаров:"""
    
    await callback.message.edit_text(
        shop_text,
        reply_markup=shop_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("shop_"))
async def show_shop_category(callback: CallbackQuery):
    """Отображение категории товаров"""
    category = callback.data.replace("shop_", "")
    
    category_names = {
        'weapons': '⚔️ Оружейная лавка',
        'armor': '🛡️ Доспехи и броня',
        'potions': '🧪 Алхимическая лавка',
        'magic': '📜 Магическая гильдия',
        'food': '🍖 Провиант'
    }
    
    items = SHOP_ITEMS.get(category, [])
    
    items_text = ""
    for item in items:
        items_text += f"\n• <b>{item['name']}</b>\n"
        items_text += f"  {item['description']}\n"
        items_text += f"  Цена: {format_currency(item['price'])}\n"
    
    shop_text = f"""<b>{category_names.get(category, 'Магазин')}</b>
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
