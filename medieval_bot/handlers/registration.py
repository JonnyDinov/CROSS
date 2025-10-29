from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from medieval_bot.database.models import User, Stats, CasinoStats
from medieval_bot.database.engine import async_session_maker
from medieval_bot.keyboards.inline import (
    race_selection_keyboard,
    class_selection_keyboard
)
from medieval_bot.keyboards.reply import main_menu_keyboard
from medieval_bot.utils.text_generator import get_random_message
from medieval_bot.config import config
from medieval_bot.constants import (
    RACE_TO_KINGDOM,
    RACE_BONUSES,
    CLASS_BONUSES,
    BASE_STATS,
    RACE_DESCRIPTIONS
)

router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    selecting_race = State()
    selecting_class = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Команда /start - начало регистрации"""
    user_id = message.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            await message.answer(
                f"С возвращением, {user.character_name}! 🏰\n\n"
                f"Выберите действие:",
                reply_markup=main_menu_keyboard()
            )
            return
    
    welcome_text = f"""⚔️ Добро пожаловать в Средневековый Мир! ⚔️

{get_random_message('welcome')}

Четыре великих королевства ждут отважных героев:

🏰 <b>Валхейм</b> - земли людей
🌲 <b>Сильвания</b> - царство эльфов
⛰️ <b>Казад-Дум</b> - горы дварфов
⚔️ <b>Кхан-Гор</b> - степи орков

Начни своё приключение! Введи имя своего персонажа:"""
    
    await message.answer(welcome_text, parse_mode="HTML")
    await state.set_state(RegistrationStates.waiting_for_name)

@router.message(RegistrationStates.waiting_for_name)
async def process_character_name(message: Message, state: FSMContext):
    """Обработка имени персонажа"""
    character_name = message.text.strip()
    
    if len(character_name) < 3 or len(character_name) > 20:
        await message.answer("Имя должно быть от 3 до 20 символов. Попробуй ещё раз:")
        return
    
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.character_name == character_name)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            await message.answer(
                "Это имя уже занято другим героем. Выбери другое имя:"
            )
            return
    
    await state.update_data(character_name=character_name)
    
    race_text = f"""Прекрасный выбор, <b>{character_name}</b>! 

Теперь выбери свою расу. Каждая раса имеет уникальные бонусы:

👤 <b>Люди</b> - универсалы, +10% к получаемой валюте
🧝 <b>Эльфы</b> - ловкость +2, магия +1, +15% к восстановлению маны
⚒️ <b>Дварфы</b> - сила +2, выносливость +2, +20% к прочности экипировки
💪 <b>Орки</b> - сила +3, выносливость +1, +15% к физическому урону

<i>Твоя раса определит, в каком королевстве ты начнёшь своё путешествие!</i>"""
    
    await message.answer(race_text, reply_markup=race_selection_keyboard(), parse_mode="HTML")
    await state.set_state(RegistrationStates.selecting_race)

@router.callback_query(F.data.startswith("race_"))
async def process_race_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора расы"""
    race = callback.data.replace("race_", "")
    kingdom = RACE_TO_KINGDOM[race]
    
    await state.update_data(race=race, kingdom=kingdom)
    
    class_text = f"""Отличный выбор! Ты станешь представителем расы <b>{race}</b>!
Твой путь начнётся в королевстве <b>{kingdom}</b>! 🏰

Теперь выбери класс персонажа:

⚔️ <b>Воин</b> - мастер ближнего боя и тяжёлой брони
🔮 <b>Маг</b> - повелитель магических сил
🏹 <b>Лучник</b> - непревзойдённый стрелок
✨ <b>Жрец</b> - целитель и защитник союзников"""
    
    await callback.message.edit_text(
        class_text,
        reply_markup=class_selection_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.selecting_class)
    await callback.answer()

@router.callback_query(F.data.startswith("class_"))
async def process_class_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора класса и завершение регистрации"""
    character_class = callback.data.replace("class_", "")
    
    data = await state.get_data()
    character_name = data['character_name']
    race = data['race']
    kingdom = data['kingdom']
    
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    race_bonus = RACE_BONUSES[race]
    class_bonus = CLASS_BONUSES[character_class]
    
    final_stats = {}
    for stat in BASE_STATS:
        final_stats[stat] = BASE_STATS[stat] + race_bonus.get(stat, 0) + class_bonus.get(stat, 0)
    
    async with async_session_maker() as session:
        new_user = User(
            user_id=user_id,
            username=username,
            character_name=character_name,
            race=race,
            character_class=character_class,
            kingdom=kingdom,
            copper_coins=config.STARTING_COPPER,
            current_location=kingdom
        )
        session.add(new_user)
        
        new_stats = Stats(
            user_id=user_id,
            strength=final_stats['strength'],
            agility=final_stats['agility'],
            intelligence=final_stats['intelligence'],
            endurance=final_stats['endurance'],
            luck=final_stats['luck'],
            health=100 + (final_stats['endurance'] * 5),
            max_health=100 + (final_stats['endurance'] * 5),
            mana=50 + (final_stats['intelligence'] * 3),
            max_mana=50 + (final_stats['intelligence'] * 3)
        )
        session.add(new_stats)
        
        casino_stats = CasinoStats(user_id=user_id)
        session.add(casino_stats)
        
        await session.commit()
    
    completion_text = f"""🎉 <b>Регистрация завершена!</b> 🎉

Приветствуем тебя, <b>{character_name}</b>!

📜 <b>Твой профиль:</b>
🧬 Раса: {race}
🛡️ Класс: {character_class}
🏰 Королевство: {kingdom}

📊 <b>Характеристики:</b>
💪 Сила: {final_stats['strength']}
🏃 Ловкость: {final_stats['agility']}
🧠 Интеллект: {final_stats['intelligence']}
❤️ Выносливость: {final_stats['endurance']}
🍀 Удача: {final_stats['luck']}

💰 <b>Стартовый капитал:</b>
🟤 {config.STARTING_COPPER} медных монет

Твоё приключение начинается! Выбери действие:"""
    
    await callback.message.edit_text(
        completion_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()
    await callback.answer("Добро пожаловать в игру! 🎮")
