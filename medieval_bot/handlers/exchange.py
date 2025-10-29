from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, update

from medieval_bot.database.models import User
from medieval_bot.database.engine import async_session_maker
from medieval_bot.keyboards.inline import (
    exchange_menu_keyboard,
    exchange_up_keyboard,
    exchange_down_keyboard,
    kingdom_menu_keyboard
)
from medieval_bot.utils.currency import format_currency, convert_from_copper

router = Router()

class ExchangeStates(StatesGroup):
    waiting_for_amount = State()

@router.callback_query(F.data == "exchange")
async def show_exchange_menu(callback: CallbackQuery):
    """Меню обмена валют"""
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.answer("Ошибка: персонаж не найден!", show_alert=True)
            return
    
    currencies = convert_from_copper(user.copper_coins)
    
    exchange_text = f"""💱 <b>Обменная лавка</b>
━━━━━━━━━━━━━━━━━━━━

"Обменяю монеты по честному курсу!"

Твой кошелёк:
{format_currency(user.copper_coins)}

Детально:
💎 {currencies['platinum']} платиновых
🟡 {currencies['gold']} золотых
⚪ {currencies['silver']} серебряных
🟤 {currencies['copper']} медных

Выбери операцию:"""
    
    await callback.message.edit_text(
        exchange_text,
        reply_markup=exchange_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "exchange_up")
async def show_exchange_up(callback: CallbackQuery):
    """Меню обмена на более ценную валюту"""
    text = """💱 <b>Обмен на более ценную валюту</b>
━━━━━━━━━━━━━━━━━━━━

Выбери направление обмена:"""
    
    await callback.message.edit_text(
        text,
        reply_markup=exchange_up_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "exchange_down")
async def show_exchange_down(callback: CallbackQuery):
    """Меню размена на мелочь"""
    text = """💱 <b>Размен на мелочь</b>
━━━━━━━━━━━━━━━━━━━━

Выбери направление обмена:"""
    
    await callback.message.edit_text(
        text,
        reply_markup=exchange_down_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "exchange_rates")
async def show_exchange_rates(callback: CallbackQuery):
    """Отображение курса обмена"""
    rates_text = """📊 <b>Курс обмена валют</b>
━━━━━━━━━━━━━━━━━━━━

<b>Официальный курс королевств:</b>

🟤 100 медных = ⚪ 1 серебряная
⚪ 100 серебряных = 🟡 1 золотая
🟡 100 золотых = 💎 1 платиновая

<b>Быстрый расчёт:</b>
🟤 10,000 медных = 🟡 1 золотая
🟤 1,000,000 медных = 💎 1 платиновая
⚪ 10,000 серебряных = 💎 1 платиновая

Курс обмена фиксированный и действует во всех королевствах!"""
    
    await callback.message.edit_text(
        rates_text,
        reply_markup=exchange_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("exchange_copper_"))
async def exchange_copper_to_silver(callback: CallbackQuery):
    """Обмен меди на серебро"""
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        currencies = convert_from_copper(user.copper_coins)
        copper_available = currencies['copper']
        
        if copper_available < 100:
            await callback.answer(
                f"Недостаточно медных монет! Нужно минимум 100, у тебя {copper_available}",
                show_alert=True
            )
            return
        
        silver_to_get = copper_available // 100
        copper_to_spend = silver_to_get * 100
        
        new_balance = user.copper_coins - copper_to_spend + (silver_to_get * 100)
        
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(copper_coins=new_balance)
        )
        await session.commit()
    
    result_text = f"""✅ <b>Обмен выполнен!</b>
━━━━━━━━━━━━━━━━━━━━

Обменяно:
🟤 {copper_to_spend} медных → ⚪ {silver_to_get} серебряных

Новый баланс:
{format_currency(new_balance)}"""
    
    await callback.message.edit_text(
        result_text,
        reply_markup=exchange_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("Обмен успешен! 💱")

@router.callback_query(F.data.startswith("exchange_silver_gold"))
async def exchange_silver_to_gold(callback: CallbackQuery):
    """Обмен серебра на золото"""
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        currencies = convert_from_copper(user.copper_coins)
        silver_available = currencies['silver']
        
        if silver_available < 100:
            await callback.answer(
                f"Недостаточно серебряных монет! Нужно минимум 100, у тебя {silver_available}",
                show_alert=True
            )
            return
        
        gold_to_get = silver_available // 100
        silver_to_spend = gold_to_get * 100
        copper_to_remove = silver_to_spend * 100
        copper_to_add = gold_to_get * 10000
        
        new_balance = user.copper_coins - copper_to_remove + copper_to_add
        
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(copper_coins=new_balance)
        )
        await session.commit()
    
    result_text = f"""✅ <b>Обмен выполнен!</b>
━━━━━━━━━━━━━━━━━━━━

Обменяно:
⚪ {silver_to_spend} серебряных → 🟡 {gold_to_get} золотых

Новый баланс:
{format_currency(new_balance)}"""
    
    await callback.message.edit_text(
        result_text,
        reply_markup=exchange_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("Обмен успешен! 💱")

@router.callback_query(F.data.startswith("exchange_gold_platinum"))
async def exchange_gold_to_platinum(callback: CallbackQuery):
    """Обмен золота на платину"""
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        currencies = convert_from_copper(user.copper_coins)
        gold_available = currencies['gold']
        
        if gold_available < 100:
            await callback.answer(
                f"Недостаточно золотых монет! Нужно минимум 100, у тебя {gold_available}",
                show_alert=True
            )
            return
        
        platinum_to_get = gold_available // 100
        gold_to_spend = platinum_to_get * 100
        copper_to_remove = gold_to_spend * 10000
        copper_to_add = platinum_to_get * 1000000
        
        new_balance = user.copper_coins - copper_to_remove + copper_to_add
        
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(copper_coins=new_balance)
        )
        await session.commit()
    
    result_text = f"""✅ <b>Обмен выполнен!</b>
━━━━━━━━━━━━━━━━━━━━

Обменяно:
🟡 {gold_to_spend} золотых → 💎 {platinum_to_get} платиновых

Новый баланс:
{format_currency(new_balance)}"""
    
    await callback.message.edit_text(
        result_text,
        reply_markup=exchange_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("Обмен успешен! 💱")

@router.callback_query(F.data.startswith("exchange_platinum_gold"))
async def exchange_platinum_to_gold(callback: CallbackQuery):
    """Размен платины на золото"""
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        currencies = convert_from_copper(user.copper_coins)
        platinum_available = currencies['platinum']
        
        if platinum_available < 1:
            await callback.answer("У тебя нет платиновых монет для размена!", show_alert=True)
            return
        
        await callback.message.answer(
            f"💎 У тебя {platinum_available} платиновых монет.\n"
            f"Сколько разменять? (1 💎 = 100 🟡)\n\n"
            f"<i>Напиши количество платины для размена (или 0 для отмены):</i>",
            parse_mode="HTML"
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("exchange_gold_silver"))
async def exchange_gold_to_silver(callback: CallbackQuery):
    """Размен золота на серебро"""
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        currencies = convert_from_copper(user.copper_coins)
        gold_available = currencies['gold']
        
        if gold_available < 1:
            await callback.answer("У тебя нет золотых монет для размена!", show_alert=True)
            return
        
        await callback.answer("Размен золота пока недоступен. Используй обратный обмен через серебро!", show_alert=True)

@router.callback_query(F.data.startswith("exchange_silver_copper"))
async def exchange_silver_to_copper(callback: CallbackQuery):
    """Размен серебра на медь"""
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        currencies = convert_from_copper(user.copper_coins)
        silver_available = currencies['silver']
        
        if silver_available < 1:
            await callback.answer("У тебя нет серебряных монет для размена!", show_alert=True)
            return
        
        await callback.answer("Размен серебра пока недоступен. Используй обратный обмен через медь!", show_alert=True)
