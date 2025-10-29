from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, update

from medieval_bot.database.models import User
from medieval_bot.database.engine import async_session_maker
from medieval_bot.keyboards.reply import main_menu_keyboard
from medieval_bot.utils.currency import format_currency
from medieval_bot.constants import TRAVEL_COSTS

router = Router()

@router.callback_query(F.data.startswith("travel_"))
async def process_travel(callback: CallbackQuery):
    """Обработка путешествия"""
    destination = callback.data.replace("travel_", "")
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.answer("Ошибка: персонаж не найден!", show_alert=True)
            return
        
        current_location = user.current_location or user.kingdom
        
        if current_location == destination:
            await callback.answer("Ты уже находишься в этом королевстве!", show_alert=True)
            return
        
        travel_cost = TRAVEL_COSTS.get(destination, 1000)
        
        if user.copper_coins < travel_cost:
            needed = format_currency(travel_cost - user.copper_coins)
            await callback.answer(
                f"Недостаточно средств! Нужно ещё {needed}",
                show_alert=True
            )
            return
        
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(
                copper_coins=user.copper_coins - travel_cost,
                current_location=destination
            )
        )
        await session.commit()
    
    travel_complete_text = f"""🗺️ <b>Путешествие завершено!</b>
━━━━━━━━━━━━━━━━━━━━

Ты успешно добрался до <b>{destination}</b>!

Стоимость путешествия: {format_currency(travel_cost)}
Осталось средств: {format_currency(user.copper_coins - travel_cost)}

<i>Добро пожаловать в {destination}! Исследуй новые земли и знакомься с местными жителями.</i>

Используй кнопки меню ниже для продолжения приключения! 🏰"""
    
    await callback.message.answer(
        travel_complete_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("Удачного путешествия! 🗺️")
