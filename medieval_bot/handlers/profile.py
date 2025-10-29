from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from medieval_bot.database.models import User, Stats, CasinoStats
from medieval_bot.database.engine import async_session_maker
from medieval_bot.keyboards.inline import main_menu_keyboard
from medieval_bot.utils.currency import format_currency

router = Router()

@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    """Отображение профиля игрока"""
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            await callback.answer("Ошибка: персонаж не найден!", show_alert=True)
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
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "inventory")
async def show_inventory(callback: CallbackQuery):
    """Отображение инвентаря"""
    inventory_text = """🎒 <b>Инвентарь</b>
━━━━━━━━━━━━━━━━━━━━

Твой инвентарь пока пуст.
Посети магазины в королевстве, чтобы приобрести снаряжение!

<i>Эта функция будет доступна в следующих обновлениях.</i>"""
    
    await callback.message.edit_text(
        inventory_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "quests")
async def show_quests(callback: CallbackQuery):
    """Отображение квестов"""
    quests_text = """⚔️ <b>Квесты</b>
━━━━━━━━━━━━━━━━━━━━

В данный момент у тебя нет активных квестов.

Посети Тронный зал в своём королевстве, чтобы получить задания от правителя!

<i>Система квестов будет добавлена в следующих обновлениях.</i>"""
    
    await callback.message.edit_text(
        quests_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "craft")
async def show_craft(callback: CallbackQuery):
    """Отображение крафта"""
    craft_text = """⚒️ <b>Крафт</b>
━━━━━━━━━━━━━━━━━━━━

Собирай ресурсы и создавай уникальные предметы!

Посети кузницу в королевстве, чтобы узнать больше о доступных рецептах.

<i>Система крафта будет добавлена в следующих обновлениях.</i>"""
    
    await callback.message.edit_text(
        craft_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
