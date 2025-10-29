# 🔌 Bot API Reference

Внутреннее API бота для разработчиков.

## 💾 Database API

### User Management

```python
from medieval_bot.database.engine import async_session_maker
from medieval_bot.database.models import User
from sqlalchemy import select

# Получить пользователя
async with async_session_maker() as session:
    result = await session.execute(
        select(User).where(User.user_id == telegram_user_id)
    )
    user = result.scalar_one_or_none()

# Создать пользователя
new_user = User(
    user_id=telegram_user_id,
    username=telegram_username,
    character_name="Hero",
    race="Люди",
    character_class="Воин",
    kingdom="Валхейм",
    copper_coins=500
)
session.add(new_user)
await session.commit()

# Обновить баланс
from sqlalchemy import update
await session.execute(
    update(User)
    .where(User.user_id == telegram_user_id)
    .values(copper_coins=new_amount)
)
await session.commit()
```

### Stats Management

```python
from medieval_bot.database.models import Stats

# Получить характеристики
result = await session.execute(
    select(Stats).where(Stats.user_id == telegram_user_id)
)
stats = result.scalar_one_or_none()

# Создать характеристики
new_stats = Stats(
    user_id=telegram_user_id,
    strength=10,
    agility=10,
    intelligence=10,
    endurance=10,
    luck=10,
    health=100,
    max_health=100
)
session.add(new_stats)
await session.commit()
```

### Casino Stats

```python
from medieval_bot.database.models import CasinoStats

# Обновить статистику после игры
casino_stats.games_played += 1
if won:
    casino_stats.total_won += winnings
    casino_stats.current_streak += 1
    if winnings > casino_stats.biggest_win:
        casino_stats.biggest_win = winnings
else:
    casino_stats.total_lost += losses
    casino_stats.current_streak = 0

await session.commit()
```

## 💰 Currency API

```python
from medieval_bot.utils.currency import (
    convert_to_copper,
    convert_from_copper,
    format_currency
)

# Конвертация в медь (для хранения в БД)
copper = convert_to_copper(platinum=1, gold=5, silver=50, copper=25)
# Результат: 1050525

# Конвертация из меди (для отображения)
currencies = convert_from_copper(1050525)
# Результат: {'platinum': 1, 'gold': 5, 'silver': 50, 'copper': 25}

# Форматирование для Telegram
text = format_currency(1050525)
# Результат: "💎 1 плат. 🟡 5 зол. ⚪ 50 сер. 🟤 25 мед."
```

## 🎮 Game Logic API

### Axe Throwing

```python
from medieval_bot.utils.game_logic import axe_throwing_game

zone, multiplier = axe_throwing_game(luck=15)
# zone: "🎯 Яблочко", "🟡 Внутренний круг", etc.
# multiplier: 5.0, 3.0, 2.0, 1.5, or 0.0
```

### Dice Game

```python
from medieval_bot.utils.game_logic import dice_game

dice_results, description, multiplier = dice_game()
# dice_results: [3, 3, 5]
# description: "🎲🎲 ДВА ОДИНАКОВЫХ"
# multiplier: 3.0
```

### Poker

```python
from medieval_bot.utils.game_logic import (
    generate_poker_hand,
    evaluate_poker_hand
)

hand = generate_poker_hand()
# [{'suit': '🗡️', 'rank': 'Король', 'value': 13}, ...]

combo_name, multiplier, strength = evaluate_poker_hand(hand)
# combo_name: "✌️ ПАРА"
# multiplier: 2.0
# strength: 2 (для сравнения с противником)
```

### Target Shooting

```python
from medieval_bot.utils.game_logic import target_shooting_game

hits, multiplier = target_shooting_game(agility=20)
# hits: 0-3
# multiplier: 5.0, 2.0, 1.0, or 0.0
```

### Roulette

```python
from medieval_bot.utils.game_logic import (
    roulette_spin,
    check_roulette_bet
)

number, color = roulette_spin()
# number: 0-36
# color: 'red', 'blue', or 'black'

is_win, multiplier = check_roulette_bet(
    bet_type='color',
    bet_value='red',
    result_number=24,
    result_color='red'
)
# is_win: True
# multiplier: 2.0
```

### Rune Divination

```python
from medieval_bot.utils.game_logic import rune_divination

runes, description, multiplier = rune_divination()
# runes: ['⚡', '⚡', '🌙']
# description: "🌟 ДВЕ ОДИНАКОВЫЕ РУНЫ"
# multiplier: 3.0
```

## ⌨️ Keyboard API

```python
from medieval_bot.keyboards.inline import (
    main_menu_keyboard,
    kingdom_menu_keyboard,
    casino_main_keyboard,
    currency_selection_keyboard,
    # ... и другие
)

# Использование
await message.answer(
    "Выберите действие:",
    reply_markup=main_menu_keyboard()
)

# Динамическая клавиатура путешествий
from medieval_bot.keyboards.inline import travel_menu_keyboard
keyboard = travel_menu_keyboard(current_kingdom="Валхейм")
```

## 📝 Text Generator API

```python
from medieval_bot.utils.text_generator import (
    get_random_message,
    get_kingdom_description,
    CASINO_GREETING
)

# Случайное сообщение
welcome = get_random_message('welcome')
win_msg = get_random_message('casino_win')
lose_msg = get_random_message('casino_lose')

# Описание королевства
description = get_kingdom_description("Валхейм")

# Константы
greeting = CASINO_GREETING
```

## 🎯 FSM States

### Registration States

```python
from medieval_bot.handlers.registration import RegistrationStates

# Использование
await state.set_state(RegistrationStates.waiting_for_name)
await state.set_state(RegistrationStates.selecting_race)
await state.set_state(RegistrationStates.selecting_class)
```

### Casino States

```python
from medieval_bot.handlers.casino import CasinoStates

await state.set_state(CasinoStates.selecting_currency)
await state.set_state(CasinoStates.selecting_bet_amount)
await state.set_state(CasinoStates.playing_game)

# Сохранение данных состояния
await state.update_data(
    currency='gold',
    bet_amount=10,
    current_game='poker'
)

# Получение данных
data = await state.get_data()
currency = data.get('currency', 'copper')
```

## 🎲 Casino Integration

### Создание новой игры - полный пример

```python
# 1. Добавить логику в utils/game_logic.py
def my_new_game(player_stat: int) -> Tuple[str, float]:
    """Новая игра казино"""
    import random
    
    # Логика игры
    roll = random.randint(1, 100)
    
    if roll > 90:
        return "Джекпот!", 10.0
    elif roll > 50:
        return "Выигрыш", 2.0
    else:
        return "Проигрыш", 0.0

# 2. Добавить кнопку в keyboards/inline.py
# В функции casino_main_keyboard():
[InlineKeyboardButton(
    text="🎰 Моя игра",
    callback_data="casino_mygame"
)]

# 3. Добавить обработчики в handlers/casino.py
@router.callback_query(F.data == "casino_mygame")
async def show_my_game(callback: CallbackQuery, state: FSMContext):
    await state.update_data(current_game='mygame')
    
    text = """🎰 Моя игра
━━━━━━━━━━━━━━━━━━━━

Описание игры...

Правила:
- Джекпот (10%): x10
- Выигрыш (40%): x2
- Проигрыш (50%): потеря ставки"""
    
    keyboard = game_action_keyboard('mygame')
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "play_mygame")
async def play_my_game(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    
    currency = data.get('currency', 'copper')
    bet_amount = data.get('bet_amount', 10)
    bet_in_copper = bet_amount * CURRENCY_MULTIPLIERS[currency]
    
    async with async_session_maker() as session:
        # Получить пользователя
        user_result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        # Проверить баланс
        if user.copper_coins < bet_in_copper:
            await callback.answer(
                "Недостаточно средств!",
                show_alert=True
            )
            return
        
        # Получить характеристики
        stats_result = await session.execute(
            select(Stats).where(Stats.user_id == user_id)
        )
        stats = stats_result.scalar_one_or_none()
        
        # Играть!
        result_text, multiplier = my_new_game(stats.luck)
        
        # Рассчитать выигрыш
        if multiplier > 0:
            winnings = int(bet_in_copper * multiplier) - bet_in_copper
        else:
            winnings = -bet_in_copper
        
        new_balance = user.copper_coins + winnings
        
        # Обновить баланс
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(copper_coins=new_balance)
        )
        
        # Обновить статистику казино
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
    
    # Показать результат
    if winnings > 0:
        result = f"""🎰 Результат: {result_text}
        
ПОБЕДА! 🎉
Выигрыш: {format_currency(winnings)}
Баланс: {format_currency(new_balance)}"""
    else:
        result = f"""🎰 Результат: {result_text}

Потеря: {format_currency(abs(winnings))}
Баланс: {format_currency(new_balance)}"""
    
    await callback.message.edit_text(
        result,
        reply_markup=back_to_casino_keyboard()
    )
    await callback.answer()
```

## 📊 Constants

### Расы и королевства
```python
RACE_TO_KINGDOM = {
    'Люди': 'Валхейм',
    'Эльфы': 'Сильвания',
    'Дварфы': 'Казад-Дум',
    'Орки': 'Кхан-Гор'
}
```

### Бонусы рас
```python
RACE_BONUSES = {
    'Люди': {'strength': 0, 'agility': 0, 'intelligence': 0, 'endurance': 0},
    'Эльфы': {'strength': 0, 'agility': 2, 'intelligence': 1, 'endurance': -1},
    'Дварфы': {'strength': 2, 'agility': -1, 'intelligence': 0, 'endurance': 2},
    'Орки': {'strength': 3, 'agility': 0, 'intelligence': -1, 'endurance': 1}
}
```

### Бонусы классов
```python
CLASS_BONUSES = {
    'Воин': {'strength': 3, 'agility': 1, 'intelligence': 0, 'endurance': 2},
    'Маг': {'strength': 0, 'agility': 1, 'intelligence': 4, 'endurance': 0},
    'Лучник': {'strength': 1, 'agility': 4, 'intelligence': 1, 'endurance': 0},
    'Жрец': {'strength': 0, 'agility': 0, 'intelligence': 3, 'endurance': 2}
}
```

### Множители валют
```python
CURRENCY_MULTIPLIERS = {
    'copper': 1,
    'silver': 100,
    'gold': 10000,
    'platinum': 1000000
}
```

---

**Используйте это API для расширения функционала бота! 🚀**
