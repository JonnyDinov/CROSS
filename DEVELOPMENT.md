# 🛠️ Development Guide

Руководство по разработке и расширению Medieval RPG Bot.

## 📁 Архитектура проекта

### Handlers (Обработчики)
Каждый модуль в `handlers/` отвечает за свою область:
- `registration.py` - создание персонажа
- `profile.py` - отображение профиля
- `kingdoms.py` - навигация по королевству
- `travel.py` - путешествия
- `shop.py` - магазины
- `exchange.py` - обмен валют
- `casino.py` - все игры казино

### Database Models
Все модели в `database/models.py`:
```python
User - основная информация о персонаже
Stats - характеристики
Inventory - инвентарь (placeholder)
Kingdom - королевства (4 штуки)
Shop - товары магазинов
CasinoStats - статистика игр
Achievement - достижения
```

### Utils (Утилиты)
- `currency.py` - конвертация валют (медь ↔ все валюты)
- `game_logic.py` - механика казино-игр
- `text_generator.py` - шаблоны текстов

## 🎮 Добавление новой игры в казино

### Шаг 1: Добавить логику в `utils/game_logic.py`
```python
def new_game_logic(stats_param: int) -> Tuple[result, multiplier]:
    """
    Новая игра
    Возвращает: (результат для отображения, множитель выигрыша)
    """
    # Ваша логика
    return result, multiplier
```

### Шаг 2: Добавить кнопку в `keyboards/inline.py`
```python
# В casino_main_keyboard()
[InlineKeyboardButton(text="🎪 Новая игра", callback_data="casino_newgame")]

# Создать game_action_keyboard для игры
'newgame': [
    [InlineKeyboardButton(text="🎪 Играть!", callback_data="play_newgame")]
]
```

### Шаг 3: Добавить обработчики в `handlers/casino.py`
```python
@router.callback_query(F.data == "casino_newgame")
async def show_newgame(callback: CallbackQuery, state: FSMContext):
    """Показать игру"""
    # Описание игры
    await callback.message.edit_text(...)

@router.callback_query(F.data == "play_newgame")
async def play_newgame(callback: CallbackQuery, state: FSMContext):
    """Играть в игру"""
    # 1. Проверить баланс
    # 2. Вызвать game_logic
    # 3. Обновить баланс в БД
    # 4. Обновить casino_stats
    # 5. Показать результат
```

## 💾 Работа с базой данных

### Создание новой модели
```python
# В database/models.py
class NewModel(Base):
    __tablename__ = 'new_table'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    # ...
```

### Чтение данных
```python
from sqlalchemy import select

async with async_session_maker() as session:
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
```

### Обновление данных
```python
from sqlalchemy import update

await session.execute(
    update(User)
    .where(User.user_id == user_id)
    .values(copper_coins=new_amount)
)
await session.commit()
```

### Добавление новых данных
```python
new_item = Item(user_id=user_id, name="Sword")
session.add(new_item)
await session.commit()
```

## ⚙️ Система валют

### Важно: Все валюты в БД хранятся в медных монетах!

```python
from medieval_bot.utils.currency import (
    convert_to_copper,
    convert_from_copper,
    format_currency
)

# Конвертация в медь для хранения
copper_total = convert_to_copper(
    platinum=1,
    gold=50,
    silver=75,
    copper=25
)

# Конвертация из меди для отображения
currencies = convert_from_copper(1507525)
# {'platinum': 1, 'gold': 50, 'silver': 75, 'copper': 25}

# Форматирование для отображения
text = format_currency(1507525)
# "💎 1 плат. 🟡 50 зол. ⚪ 75 сер. 🟤 25 мед."
```

## 🎯 FSM (Finite State Machine)

### Создание нового FSM
```python
from aiogram.fsm.state import State, StatesGroup

class MyStates(StatesGroup):
    step1 = State()
    step2 = State()

# Использование
await state.set_state(MyStates.step1)
await state.update_data(key="value")
data = await state.get_data()
await state.clear()
```

## 🎨 Inline Keyboards

### Создание клавиатуры
```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Кнопка 1", callback_data="btn1")],
    [
        InlineKeyboardButton(text="Кнопка 2", callback_data="btn2"),
        InlineKeyboardButton(text="Кнопка 3", callback_data="btn3")
    ]
])
```

### Обработка callback
```python
@router.callback_query(F.data == "btn1")
async def handle_button(callback: CallbackQuery):
    await callback.message.edit_text("Нажата кнопка 1")
    await callback.answer()  # Важно! Убирает "часики" в Telegram
```

## 📝 Форматирование текста

Используем HTML:
```python
text = """<b>Жирный</b>
<i>Курсив</i>
<u>Подчёркнутый</u>
<code>Моноширинный</code>
<pre>Блок кода</pre>"""

await message.answer(text, parse_mode="HTML")
```

## 🔧 Полезные команды

### Тестирование
```bash
# Тест базы данных
python test_db.py

# Запуск бота
python run.py
```

### Отладка
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Очистка БД
```bash
rm medieval_rpg.db
python test_db.py
```

## 🚀 Планы развития

### Приоритет 1 (Core Features)
- [ ] Система квестов
- [ ] Боевая система (PvE)
- [ ] Крафт и улучшение предметов
- [ ] Ежедневные бонусы

### Приоритет 2 (Social)
- [ ] Гильдии
- [ ] PvP арена
- [ ] Торговля между игроками
- [ ] Чат в таверне

### Приоритет 3 (Events)
- [ ] Сезонные события
- [ ] Турниры казино
- [ ] Мировые боссы
- [ ] Еженедельные челленджи

### Приоритет 4 (Economy)
- [ ] Аукцион
- [ ] Инвестиции в королевство
- [ ] Недвижимость
- [ ] Банковская система

## 🐛 Частые проблемы

### База данных не создаётся
```bash
# Убедитесь что установлен aiosqlite
pip install aiosqlite
```

### Бот не отвечает
- Проверьте токен в `config.py`
- Проверьте интернет-соединение
- Проверьте логи

### Ошибки импорта
```bash
# Запускайте из корневой папки проекта
cd /path/to/medieval_rpg_bot
python -m medieval_bot.bot
```

## 📚 Полезные ресурсы

- [aiogram 3 документация](https://docs.aiogram.dev/)
- [SQLAlchemy документация](https://docs.sqlalchemy.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 🤝 Contributing

1. Fork репозиторий
2. Создайте ветку: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Создайте Pull Request

## 📄 Code Style

- Используйте async/await
- Добавляйте docstrings к функциям
- Следуйте PEP 8
- Тексты на русском в средневековом стиле
- Используйте эмодзи для UI

## 🎨 Design Guidelines

### Эмодзи для UI
- 🏰 Королевство
- ⚔️ Бой/Оружие
- 🛡️ Защита
- 🎲 Казино
- 💰 Деньги
- 👤 Профиль
- 🗺️ Путешествия
- 📜 Квесты

### Тексты
- Приветствия: торжественные
- Описания: атмосферные
- Ошибки: вежливые
- Выигрыши: праздничные
- Проигрыши: ободряющие

---

**Happy Coding! 🎮**
