from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, update
from datetime import datetime, timedelta

from medieval_bot.database.models import User, Stats, CasinoStats
from medieval_bot.database.engine import async_session_maker
from medieval_bot.keyboards.inline import (
    casino_main_keyboard,
    currency_selection_keyboard,
    back_to_casino_keyboard,
    game_action_keyboard,
    main_menu_keyboard
)
from medieval_bot.utils.currency import format_currency, convert_from_copper, convert_to_copper
from medieval_bot.utils.text_generator import get_random_message, CASINO_GREETING
from medieval_bot.utils.game_logic import (
    axe_throwing_game,
    dice_game,
    generate_poker_hand,
    evaluate_poker_hand,
    target_shooting_game,
    roulette_spin,
    check_roulette_bet,
    rune_divination
)
from medieval_bot.config import config

router = Router()

class CasinoStates(StatesGroup):
    selecting_currency = State()
    selecting_bet_amount = State()
    playing_game = State()

CURRENCY_MULTIPLIERS = {
    'copper': 1,
    'silver': 100,
    'gold': 10000,
    'platinum': 1000000
}

@router.callback_query(F.data == "casino_main")
async def show_casino_main(callback: CallbackQuery, state: FSMContext):
    """Главное меню казино"""
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalar_one_or_none()
        
        casino_result = await session.execute(
            select(CasinoStats).where(CasinoStats.user_id == user_id)
        )
        casino_stats = casino_result.scalar_one_or_none()
        
        if not casino_stats:
            casino_stats = CasinoStats(user_id=user_id)
            session.add(casino_stats)
            await session.commit()
    
    current_state = await state.get_data()
    selected_currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    casino_text = f"""{CASINO_GREETING}

Твой кошелёк:
💰 {format_currency(user.copper_coins)}

📊 <b>Твоя статистика:</b>
Игр сыграно: {casino_stats.games_played}
Выиграно: {format_currency(casino_stats.total_won)}
Проиграно: {format_currency(casino_stats.total_lost)}
Самый крупный выигрыш: {format_currency(casino_stats.biggest_win)}

💰 Текущая ставка: {bet_amount} {selected_currency}

Выбери игру:"""
    
    await callback.message.edit_text(
        casino_text,
        reply_markup=casino_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "casino_currency")
async def show_currency_selection(callback: CallbackQuery):
    """Выбор валюты для ставок"""
    currency_text = """💰 <b>Выбор валюты ставки</b>
━━━━━━━━━━━━━━━━━━━━

Чем выше валюта - тем больше выигрыш!

<b>Лимиты ставок:</b>
🟤 Медный стол: 1-99 монет
⚪ Серебряный стол: 1-99 монет
🟡 Золотой стол: 1-99 монет
💎 Платиновый стол: 1-10 монет

Выбери стол для игры:"""
    
    await callback.message.edit_text(
        currency_text,
        reply_markup=currency_selection_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("currency_"))
async def select_currency(callback: CallbackQuery, state: FSMContext):
    """Установка выбранной валюты"""
    currency = callback.data.replace("currency_", "")
    
    default_bets = {
        'copper': 10,
        'silver': 5,
        'gold': 1,
        'platinum': 1
    }
    
    await state.update_data(
        currency=currency,
        bet_amount=default_bets[currency]
    )
    
    currency_names = {
        'copper': 'Медный 🟤',
        'silver': 'Серебряный ⚪',
        'gold': 'Золотой 🟡',
        'platinum': 'Платиновый 💎'
    }
    
    await callback.answer(
        f"Выбран {currency_names[currency]} стол! Ставка: {default_bets[currency]} монет",
        show_alert=True
    )
    
    await show_casino_main(callback, state)

@router.callback_query(F.data == "casino_axe")
async def show_axe_game(callback: CallbackQuery, state: FSMContext):
    """Игра: Метание топоров"""
    await state.update_data(current_game='axe')
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    game_text = f"""🎯 <b>Метание топоров</b>
━━━━━━━━━━━━━━━━━━━━

Брось топор в мишень! Чем ближе к центру - тем больше выигрыш!

<b>Зоны попадания:</b>
🎯 Яблочко (центр): x5 к ставке
🟡 Внутренний круг: x3 к ставке
🟠 Средний круг: x2 к ставке
🔴 Внешний круг: x1.5 к ставке
⚫ Промах: потеря ставки

Текущая ставка: {bet_amount} {currency}

<i>Характеристика "Удача" увеличивает шанс попадания!</i>"""
    
    await callback.message.edit_text(
        game_text,
        reply_markup=game_action_keyboard('axe'),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "play_axe_throw")
async def play_axe_throw(callback: CallbackQuery, state: FSMContext):
    """Играть в метание топоров"""
    user_id = callback.from_user.id
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    bet_in_copper = bet_amount * CURRENCY_MULTIPLIERS[currency]
    
    async with async_session_maker() as session:
        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if user.copper_coins < bet_in_copper:
            await callback.answer("Недостаточно средств для ставки!", show_alert=True)
            return
        
        stats_result = await session.execute(select(Stats).where(Stats.user_id == user_id))
        stats = stats_result.scalar_one_or_none()
        
        zone, multiplier = axe_throwing_game(stats.luck)
        
        winnings = int(bet_in_copper * multiplier) - bet_in_copper if multiplier > 0 else -bet_in_copper
        new_balance = user.copper_coins + winnings
        
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(copper_coins=new_balance)
        )
        
        casino_result = await session.execute(
            select(CasinoStats).where(CasinoStats.user_id == user_id)
        )
        casino_stats = casino_result.scalar_one_or_none()
        
        casino_stats.games_played += 1
        if winnings > 0:
            casino_stats.total_won += winnings
            casino_stats.current_streak += 1
            if winnings > casino_stats.biggest_win:
                casino_stats.biggest_win = winnings
            if casino_stats.current_streak > casino_stats.lucky_streak:
                casino_stats.lucky_streak = casino_stats.current_streak
        else:
            casino_stats.total_lost += abs(winnings)
            casino_stats.current_streak = 0
        
        casino_stats.last_game_time = datetime.now()
        
        await session.commit()
    
    if winnings > 0:
        result_text = f"""🎯 <b>Метание топоров - Результат</b>
━━━━━━━━━━━━━━━━━━━━
      🎯
   ⚫⚫⚫
  ⚫🟡⚫
   ⚫⚫⚫

Попадание: {zone}!
Множитель: x{multiplier}

{get_random_message('casino_win')}

Выигрыш: {format_currency(winnings)}
Новый баланс: {format_currency(new_balance)}"""
    else:
        result_text = f"""🎯 <b>Метание топоров - Результат</b>
━━━━━━━━━━━━━━━━━━━━
      🎯
   ⚫⚫⚫
  ⚫⚫⚫
   ⚫⚫⚫

Попадание: {zone}

{get_random_message('casino_lose')}

Потеря: {format_currency(abs(winnings))}
Новый баланс: {format_currency(new_balance)}"""
    
    await callback.message.edit_text(
        result_text,
        reply_markup=back_to_casino_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "casino_dice")
async def show_dice_game(callback: CallbackQuery, state: FSMContext):
    """Игра: Кости Судьбы"""
    await state.update_data(current_game='dice')
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    game_text = f"""🎲 <b>Кости Судьбы</b>
━━━━━━━━━━━━━━━━━━━━

Брось три кости! Совпадения приносят удачу!

<b>Комбинации:</b>
🎲🎲🎲 Три одинаковых: x10
🎲🎲 Два одинаковых: x3
📊 Стрит (1-2-3 или 4-5-6): x5
🔥 Сумма 15+: x2
❌ Остальное: потеря ставки

Текущая ставка: {bet_amount} {currency}"""
    
    await callback.message.edit_text(
        game_text,
        reply_markup=game_action_keyboard('dice'),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "play_dice_roll")
async def play_dice_roll(callback: CallbackQuery, state: FSMContext):
    """Играть в кости"""
    user_id = callback.from_user.id
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    bet_in_copper = bet_amount * CURRENCY_MULTIPLIERS[currency]
    
    async with async_session_maker() as session:
        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if user.copper_coins < bet_in_copper:
            await callback.answer("Недостаточно средств для ставки!", show_alert=True)
            return
        
        dice_results, description, multiplier = dice_game()
        
        winnings = int(bet_in_copper * multiplier) - bet_in_copper if multiplier > 0 else -bet_in_copper
        new_balance = user.copper_coins + winnings
        
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(copper_coins=new_balance)
        )
        
        casino_result = await session.execute(
            select(CasinoStats).where(CasinoStats.user_id == user_id)
        )
        casino_stats = casino_result.scalar_one_or_none()
        
        casino_stats.games_played += 1
        if winnings > 0:
            casino_stats.total_won += winnings
            casino_stats.current_streak += 1
            if winnings > casino_stats.biggest_win:
                casino_stats.biggest_win = winnings
        else:
            casino_stats.total_lost += abs(winnings)
            casino_stats.current_streak = 0
        
        await session.commit()
    
    dice_emoji = " ".join([f"🎲({d})" for d in dice_results])
    
    if winnings > 0:
        result_text = f"""🎲 <b>Кости Судьбы - Результат</b>
━━━━━━━━━━━━━━━━━━━━

Твой бросок:
{dice_emoji}

Результат: {description}
Множитель: x{multiplier}

{get_random_message('casino_win')}

Выигрыш: {format_currency(winnings)}
Новый баланс: {format_currency(new_balance)}"""
    else:
        result_text = f"""🎲 <b>Кости Судьбы - Результат</b>
━━━━━━━━━━━━━━━━━━━━

Твой бросок:
{dice_emoji}

Результат: {description}

{get_random_message('casino_lose')}

Потеря: {format_currency(abs(winnings))}
Новый баланс: {format_currency(new_balance)}"""
    
    await callback.message.edit_text(
        result_text,
        reply_markup=back_to_casino_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "casino_poker")
async def show_poker_game(callback: CallbackQuery, state: FSMContext):
    """Игра: Рыцарский покер"""
    await state.update_data(current_game='poker')
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    game_text = f"""🃏 <b>Рыцарский покер</b>
━━━━━━━━━━━━━━━━━━━━

Собери лучшую комбинацию из 5 карт!

<b>Масти:</b> 🗡️ Мечи | ⚔️ Клинки | 🛡️ Щиты | 🏹 Луки

<b>Комбинации:</b>
🏆 Роял-флеш: x100
⚡ Стрит-флеш: x50
🎰 Каре: x25
🏠 Фулл-хаус: x15
💎 Флеш: x10
📊 Стрит: x7
🎲 Тройка: x5
👥 Две пары: x3
✌️ Пара: x2

Текущая ставка: {bet_amount} {currency}"""
    
    await callback.message.edit_text(
        game_text,
        reply_markup=game_action_keyboard('poker'),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "play_poker_deal")
async def play_poker_deal(callback: CallbackQuery, state: FSMContext):
    """Играть в покер"""
    user_id = callback.from_user.id
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    bet_in_copper = bet_amount * CURRENCY_MULTIPLIERS[currency]
    
    async with async_session_maker() as session:
        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if user.copper_coins < bet_in_copper:
            await callback.answer("Недостаточно средств для ставки!", show_alert=True)
            return
        
        player_hand = generate_poker_hand()
        opponent_hand = generate_poker_hand()
        
        player_combo, player_mult, player_strength = evaluate_poker_hand(player_hand)
        opponent_combo, opponent_mult, opponent_strength = evaluate_poker_hand(opponent_hand)
        
        if player_strength > opponent_strength:
            multiplier = player_mult
            result = "ПОБЕДА"
        elif player_strength < opponent_strength:
            multiplier = 0
            result = "ПОРАЖЕНИЕ"
        else:
            multiplier = 1
            result = "НИЧЬЯ"
        
        winnings = int(bet_in_copper * multiplier) - bet_in_copper if multiplier > 0 else -bet_in_copper
        new_balance = user.copper_coins + winnings
        
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(copper_coins=new_balance)
        )
        
        casino_result = await session.execute(
            select(CasinoStats).where(CasinoStats.user_id == user_id)
        )
        casino_stats = casino_result.scalar_one_or_none()
        
        casino_stats.games_played += 1
        if winnings > 0:
            casino_stats.total_won += winnings
            casino_stats.current_streak += 1
            if winnings > casino_stats.biggest_win:
                casino_stats.biggest_win = winnings
        else:
            casino_stats.total_lost += abs(winnings)
            casino_stats.current_streak = 0
        
        await session.commit()
    
    player_cards = "\n".join([f"{c['suit']} {c['rank']}" for c in player_hand])
    opponent_cards = "\n".join([f"{c['suit']} {c['rank']}" for c in opponent_hand])
    
    if winnings > 0:
        result_text = f"""🃏 <b>Рыцарский покер - Результат</b>
━━━━━━━━━━━━━━━━━━━━

<b>Твои карты:</b>
{player_cards}
{player_combo}

<b>Карты противника:</b>
{opponent_cards}
{opponent_combo}

<b>{result}! 🏆</b>

{get_random_message('casino_win')}

Выигрыш: {format_currency(winnings)}
Новый баланс: {format_currency(new_balance)}"""
    else:
        result_text = f"""🃏 <b>Рыцарский покер - Результат</b>
━━━━━━━━━━━━━━━━━━━━

<b>Твои карты:</b>
{player_cards}
{player_combo}

<b>Карты противника:</b>
{opponent_cards}
{opponent_combo}

<b>{result}</b>

{get_random_message('casino_lose')}

Потеря: {format_currency(abs(winnings))}
Новый баланс: {format_currency(new_balance)}"""
    
    await callback.message.edit_text(
        result_text,
        reply_markup=back_to_casino_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "casino_shooting")
async def show_shooting_game(callback: CallbackQuery, state: FSMContext):
    """Игра: Стрельба по мишеням"""
    await state.update_data(current_game='shooting')
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    game_text = f"""🏹 <b>Стрельба по мишеням</b>
━━━━━━━━━━━━━━━━━━━━

Попади в движущиеся мишени! 3 попытки!

<b>Результаты:</b>
3/3 попадания: x5 к ставке
2/3 попадания: x2 к ставке
1/3 попадание: x1 (возврат ставки)
0/3 попаданий: потеря ставки

Текущая ставка: {bet_amount} {currency}

<i>Характеристика "Ловкость" увеличивает шанс попадания!</i>"""
    
    await callback.message.edit_text(
        game_text,
        reply_markup=game_action_keyboard('shooting'),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "play_shooting_start")
async def play_shooting_start(callback: CallbackQuery, state: FSMContext):
    """Играть в стрельбу"""
    user_id = callback.from_user.id
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    bet_in_copper = bet_amount * CURRENCY_MULTIPLIERS[currency]
    
    async with async_session_maker() as session:
        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if user.copper_coins < bet_in_copper:
            await callback.answer("Недостаточно средств для ставки!", show_alert=True)
            return
        
        stats_result = await session.execute(select(Stats).where(Stats.user_id == user_id))
        stats = stats_result.scalar_one_or_none()
        
        hits, multiplier = target_shooting_game(stats.agility)
        
        winnings = int(bet_in_copper * multiplier) - bet_in_copper if multiplier > 0 else -bet_in_copper
        new_balance = user.copper_coins + winnings
        
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(copper_coins=new_balance)
        )
        
        casino_result = await session.execute(
            select(CasinoStats).where(CasinoStats.user_id == user_id)
        )
        casino_stats = casino_result.scalar_one_or_none()
        
        casino_stats.games_played += 1
        if winnings > 0:
            casino_stats.total_won += winnings
            casino_stats.current_streak += 1
            if winnings > casino_stats.biggest_win:
                casino_stats.biggest_win = winnings
        else:
            casino_stats.total_lost += abs(winnings)
            casino_stats.current_streak = 0
        
        await session.commit()
    
    hit_visual = "💥 " * hits + "❌ " * (3 - hits)
    
    if winnings > 0:
        result_text = f"""🏹 <b>Стрельба по мишеням - Результат</b>
━━━━━━━━━━━━━━━━━━━━

{hit_visual}

ФИНАЛЬНЫЙ СЧЁТ: {hits}/3 попадания
Множитель: x{multiplier}

{get_random_message('casino_win')}

Выигрыш: {format_currency(winnings)}
Новый баланс: {format_currency(new_balance)}"""
    else:
        result_text = f"""🏹 <b>Стрельба по мишеням - Результат</b>
━━━━━━━━━━━━━━━━━━━━

{hit_visual}

ФИНАЛЬНЫЙ СЧЁТ: {hits}/3 попадания

{get_random_message('casino_lose')}

Потеря: {format_currency(abs(winnings))}
Новый баланс: {format_currency(new_balance)}"""
    
    await callback.message.edit_text(
        result_text,
        reply_markup=back_to_casino_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "casino_roulette")
async def show_roulette_game(callback: CallbackQuery, state: FSMContext):
    """Игра: Гладиаторская рулетка"""
    await state.update_data(current_game='roulette')
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    game_text = f"""⚔️ <b>Гладиаторская рулетка</b>
━━━━━━━━━━━━━━━━━━━━

Поставь на исход гладиаторского боя!

<b>Ставки:</b>
🔴 Красный цвет: x2
🔵 Синий цвет: x2
⚫ Чёрный (0): x10

<b>Колесо:</b> 36 секторов + 0

Текущая ставка: {bet_amount} {currency}

Выбери цвет для ставки:"""
    
    await callback.message.edit_text(
        game_text,
        reply_markup=game_action_keyboard('roulette'),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("roulette_"))
async def play_roulette(callback: CallbackQuery, state: FSMContext):
    """Играть в рулетку"""
    bet_type = callback.data.replace("roulette_", "")
    user_id = callback.from_user.id
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    bet_in_copper = bet_amount * CURRENCY_MULTIPLIERS[currency]
    
    async with async_session_maker() as session:
        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if user.copper_coins < bet_in_copper:
            await callback.answer("Недостаточно средств для ставки!", show_alert=True)
            return
        
        result_number, result_color = roulette_spin()
        
        is_win, multiplier = check_roulette_bet(
            'color' if bet_type in ['red', 'blue'] else 'zero',
            bet_type,
            result_number,
            result_color
        )
        
        winnings = int(bet_in_copper * multiplier) - bet_in_copper if is_win else -bet_in_copper
        new_balance = user.copper_coins + winnings
        
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(copper_coins=new_balance)
        )
        
        casino_result = await session.execute(
            select(CasinoStats).where(CasinoStats.user_id == user_id)
        )
        casino_stats = casino_result.scalar_one_or_none()
        
        casino_stats.games_played += 1
        if winnings > 0:
            casino_stats.total_won += winnings
            casino_stats.current_streak += 1
            if winnings > casino_stats.biggest_win:
                casino_stats.biggest_win = winnings
        else:
            casino_stats.total_lost += abs(winnings)
            casino_stats.current_streak = 0
        
        await session.commit()
    
    color_emoji = {'red': '🔴', 'blue': '🔵', 'black': '⚫'}
    bet_names = {'red': 'Красный', 'blue': 'Синий', 'zero': 'Ноль'}
    
    if winnings > 0:
        result_text = f"""⚔️ <b>Гладиаторская рулетка - Результат</b>
━━━━━━━━━━━━━━━━━━━━

⚔️ БОЙ ЗАВЕРШЁН! ⚔️

🔄 Колесо остановилось на:
{color_emoji[result_color]} Номер {result_number}

Твоя ставка: {bet_names[bet_type]}
<b>ПОБЕДА! 🏆</b>

{get_random_message('casino_win')}

Выигрыш: {format_currency(winnings)}
Новый баланс: {format_currency(new_balance)}"""
    else:
        result_text = f"""⚔️ <b>Гладиаторская рулетка - Результат</b>
━━━━━━━━━━━━━━━━━━━━

⚔️ БОЙ ЗАВЕРШЁН! ⚔️

🔄 Колесо остановилось на:
{color_emoji[result_color]} Номер {result_number}

Твоя ставка: {bet_names[bet_type]}
<b>ПОРАЖЕНИЕ</b>

{get_random_message('casino_lose')}

Потеря: {format_currency(abs(winnings))}
Новый баланс: {format_currency(new_balance)}"""
    
    await callback.message.edit_text(
        result_text,
        reply_markup=back_to_casino_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "casino_runes")
async def show_runes_game(callback: CallbackQuery, state: FSMContext):
    """Игра: Гадание на рунах"""
    await state.update_data(current_game='runes')
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    game_text = f"""🔮 <b>Гадание на рунах</b>
━━━━━━━━━━━━━━━━━━━━

Древние руны откроют твою судьбу...

<b>Руны:</b>
⚡ Мощь | 🌙 Удача | 🛡️ Защита | ❤️ Жизнь | 💀 Смерть

<b>Комбинации:</b>
Три одинаковые: x10
Две одинаковые: x3
Все разные (без 💀): x2
Есть 💀: потеря ставки

Текущая ставка: {bet_amount} {currency}"""
    
    await callback.message.edit_text(
        game_text,
        reply_markup=game_action_keyboard('runes'),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "play_runes_divine")
async def play_runes_divine(callback: CallbackQuery, state: FSMContext):
    """Играть в гадание на рунах"""
    user_id = callback.from_user.id
    
    current_state = await state.get_data()
    currency = current_state.get('currency', 'copper')
    bet_amount = current_state.get('bet_amount', 10)
    
    bet_in_copper = bet_amount * CURRENCY_MULTIPLIERS[currency]
    
    async with async_session_maker() as session:
        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if user.copper_coins < bet_in_copper:
            await callback.answer("Недостаточно средств для ставки!", show_alert=True)
            return
        
        runes, description, multiplier = rune_divination()
        
        winnings = int(bet_in_copper * multiplier) - bet_in_copper if multiplier > 0 else -bet_in_copper
        new_balance = user.copper_coins + winnings
        
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(copper_coins=new_balance)
        )
        
        casino_result = await session.execute(
            select(CasinoStats).where(CasinoStats.user_id == user_id)
        )
        casino_stats = casino_result.scalar_one_or_none()
        
        casino_stats.games_played += 1
        if winnings > 0:
            casino_stats.total_won += winnings
            casino_stats.current_streak += 1
            if winnings > casino_stats.biggest_win:
                casino_stats.biggest_win = winnings
        else:
            casino_stats.total_lost += abs(winnings)
            casino_stats.current_streak = 0
        
        await session.commit()
    
    runes_visual = " | ".join(runes)
    
    if winnings > 0:
        result_text = f"""🔮 <b>Гадание на рунах - Результат</b>
━━━━━━━━━━━━━━━━━━━━

Твои руны:
{runes_visual}

{description}
Множитель: x{multiplier}

{get_random_message('casino_win')}

Выигрыш: {format_currency(winnings)}
Новый баланс: {format_currency(new_balance)}"""
    else:
        result_text = f"""🔮 <b>Гадание на рунах - Результат</b>
━━━━━━━━━━━━━━━━━━━━

Твои руны:
{runes_visual}

{description}

{get_random_message('casino_lose')}

Потеря: {format_currency(abs(winnings))}
Новый баланс: {format_currency(new_balance)}"""
    
    await callback.message.edit_text(
        result_text,
        reply_markup=back_to_casino_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "casino_rules")
async def show_casino_rules(callback: CallbackQuery):
    """Правила казино"""
    rules_text = """📜 <b>Правила Зала Удачи</b>
━━━━━━━━━━━━━━━━━━━━

<b>Общие правила:</b>
• Выбери валюту для ставок
• Делай ставки в пределах лимитов
• Твои характеристики влияют на шансы
• Удача переменчива - играй с умом!

<b>Влияние характеристик:</b>
🍀 Удача - помогает в метании топоров
🏃 Ловкость - повышает меткость стрельбы
🧠 Интеллект - нет влияния (пока)

<b>Советы:</b>
• Начинай с малых ставок
• Следи за балансом
• Не гонись за потерями
• Остановись вовремя!

Удачи в играх! 🎲"""
    
    await callback.message.edit_text(
        rules_text,
        reply_markup=casino_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "casino_play_again")
async def casino_play_again(callback: CallbackQuery, state: FSMContext):
    """Играть ещё раз в ту же игру"""
    current_state = await state.get_data()
    current_game = current_state.get('current_game')
    
    if not current_game:
        await show_casino_main(callback, state)
        return
    
    game_handlers = {
        'axe': show_axe_game,
        'dice': show_dice_game,
        'poker': show_poker_game,
        'shooting': show_shooting_game,
        'roulette': show_roulette_game,
        'runes': show_runes_game
    }
    
    handler = game_handlers.get(current_game)
    if handler:
        await handler(callback, state)
    else:
        await show_casino_main(callback, state)

@router.callback_query(F.data == "casino_change_bet")
async def casino_change_bet(callback: CallbackQuery):
    """Изменить ставку"""
    await callback.answer(
        "Используй кнопку '💰 Выбрать валюту ставки' в главном меню казино для изменения ставок!",
        show_alert=True
    )
