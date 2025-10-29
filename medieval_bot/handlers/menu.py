from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Text
from sqlalchemy import select

from medieval_bot.database.models import User
from medieval_bot.database.engine import async_session_maker
from medieval_bot.keyboards.reply import main_menu_keyboard
from medieval_bot.keyboards.inline import (
    kingdom_menu_keyboard,
    casino_main_keyboard,
    shop_menu_keyboard,
    travel_menu_keyboard
)
from medieval_bot.constants import MessageCommands
from medieval_bot.utils.text_generator import get_kingdom_description
from medieval_bot.utils.currency import format_currency

router = Router()

@router.message(F.text == MessageCommands.KINGDOM)
async def handle_kingdom(message: Message):
    """Обработка кнопки Королевство"""
    user_id = message.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("Сначала создайте персонажа командой /start")
            return
    
    kingdom_name = user.current_location or user.kingdom
    description = get_kingdom_description(kingdom_name)
    
    kingdom_text = f"""{description}
━━━━━━━━━━━━━━━━━━━━

Выберите, куда отправиться:"""
    
    await message.answer(
        kingdom_text,
        reply_markup=kingdom_menu_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text == MessageCommands.PROFILE)
async def handle_profile(message: Message):
    """Обработка кнопки Профиль"""
    from medieval_bot.database.models import Stats, CasinoStats
    
    user_id = message.from_user.id
    
    async with async_session_maker() as session:
        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            await message.answer("Сначала создайте персонажа командой /start")
            return
        
        stats_result = await session.execute(select(Stats).where(Stats.user_id == user_id))
        stats = stats_result.scalar_one_or_none()
        
        casino_result = await session.execute(
            select(CasinoStats).where(CasinoStats.user_id == user_id)
        )
        casino_stats = casino_result.scalar_one_or_none()
    
    exp_needed = user.level * 100
    
    profile_text = f"""⚔️ <b>{user.character_name}</b>
━━━━━━━━━━━━━━━━━━━━

🧬 Раса: {user.race}
🛡️ Класс: {user.character_class}
🏰 Королевство: {user.kingdom}
📍 Местоположение: {user.current_location or user.kingdom}
⭐ Уровень: {user.level} (XP: {user.experience}/{exp_needed})

📊 <b>Характеристики:</b>
💪 Сила: {stats.strength}
🏃 Ловкость: {stats.agility}
🧠 Интеллект: {stats.intelligence}
❤️ Выносливость: {stats.endurance}
🍀 Удача: {stats.luck}

💚 Здоровье: {stats.health}/{stats.max_health}
💙 Мана: {stats.mana}/{stats.max_mana}
⚡ Энергия: {stats.energy}/{stats.max_energy}

💰 <b>Кошелёк:</b>
{format_currency(user.copper_coins)}

🎲 <b>Статистика казино:</b>
Игр сыграно: {casino_stats.games_played if casino_stats else 0}
Выиграно всего: {format_currency(casino_stats.total_won) if casino_stats else '🟤 0 мед.'}
Самый крупный выигрыш: {format_currency(casino_stats.biggest_win) if casino_stats else '🟤 0 мед.'}
Текущая серия: {casino_stats.current_streak if casino_stats else 0} 🔥"""
    
    await message.answer(
        profile_text,
        parse_mode="HTML"
    )

@router.message(F.text == MessageCommands.TRAVEL)
async def handle_travel(message: Message):
    """Обработка кнопки Путешествия"""
    user_id = message.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("Сначала создайте персонажа командой /start")
            return
    
    current_location = user.current_location or user.kingdom
    
    travel_text = f"""🗺️ <b>Карта мира</b>
━━━━━━━━━━━━━━━━━━━━

Твоё текущее местоположение:
📍 <b>{current_location}</b>

💰 Твой кошелёк: {format_currency(user.copper_coins)}

Выбери королевство для путешествия:

<i>Стоимость путешествия зависит от расстояния.
В чужих королевствах цены на товары выше на 20%!</i>"""
    
    await message.answer(
        travel_text,
        reply_markup=travel_menu_keyboard(current_location),
        parse_mode="HTML"
    )

@router.message(F.text == MessageCommands.INVENTORY)
async def handle_inventory(message: Message):
    """Обработка кнопки Инвентарь"""
    inventory_text = """🎒 <b>Инвентарь</b>
━━━━━━━━━━━━━━━━━━━━

Твой инвентарь пока пуст.
Посети магазины в королевстве, чтобы приобрести снаряжение!

<i>Эта функция будет доступна в следующих обновлениях.</i>"""
    
    await message.answer(
        inventory_text,
        parse_mode="HTML"
    )

@router.message(F.text == MessageCommands.SHOP)
async def handle_shop(message: Message):
    """Обработка кнопки Магазин"""
    user_id = message.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("Сначала создайте персонажа командой /start")
            return
    
    shop_text = f"""🏪 <b>Торговая улица</b>
━━━━━━━━━━━━━━━━━━━━

Твой кошелёк:
💰 {format_currency(user.copper_coins)}

Добро пожаловать на торговую улицу!
Здесь ты можешь приобрести всё необходимое для приключений.

Выбери категорию товаров:"""
    
    await message.answer(
        shop_text,
        reply_markup=shop_menu_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text == MessageCommands.QUESTS)
async def handle_quests(message: Message):
    """Обработка кнопки Квесты"""
    quests_text = """⚔️ <b>Квесты</b>
━━━━━━━━━━━━━━━━━━━━

В данный момент у тебя нет активных квестов.

Посети Тронный зал в своём королевстве, чтобы получить задания от правителя!

<i>Система квестов будет добавлена в следующих обновлениях.</i>"""
    
    await message.answer(
        quests_text,
        parse_mode="HTML"
    )

@router.message(F.text == MessageCommands.CASINO)
async def handle_casino(message: Message):
    """Обработка кнопки Зал Удачи"""
    from medieval_bot.database.models import CasinoStats
    from medieval_bot.utils.text_generator import CASINO_GREETING
    
    user_id = message.from_user.id
    
    async with async_session_maker() as session:
        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            await message.answer("Сначала создайте персонажа командой /start")
            return
        
        casino_result = await session.execute(
            select(CasinoStats).where(CasinoStats.user_id == user_id)
        )
        casino_stats = casino_result.scalar_one_or_none()
        
        if not casino_stats:
            casino_stats = CasinoStats(user_id=user_id)
            session.add(casino_stats)
            await session.commit()
    
    casino_text = f"""{CASINO_GREETING}

Твой кошелёк:
💰 {format_currency(user.copper_coins)}

📊 <b>Твоя статистика:</b>
Игр сыграно: {casino_stats.games_played}
Выиграно: {format_currency(casino_stats.total_won)}
Проиграно: {format_currency(casino_stats.total_lost)}
Самый крупный выигрыш: {format_currency(casino_stats.biggest_win)}

Выбери игру:"""
    
    await message.answer(
        casino_text,
        reply_markup=casino_main_keyboard(),
        parse_mode="HTML"
    )
