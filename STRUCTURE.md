# 📁 Project Structure

Визуальная структура Medieval RPG Telegram Bot.

## 🌳 Directory Tree

```
medieval_rpg_bot/
│
├── 📄 README.md                    # Основная документация
├── 📄 QUICKSTART.md                # Быстрый старт
├── 📄 GAMES.md                     # Описание игр казино
├── 📄 DEVELOPMENT.md               # Руководство разработчика
├── 📄 API.md                       # API Reference
├── 📄 PROJECT_STATUS.md            # Статус проекта
├── 📄 CHANGELOG.md                 # История изменений
├── 📄 STRUCTURE.md                 # Этот файл
├── 📄 LICENSE                      # MIT License
│
├── 📄 requirements.txt             # Зависимости Python
├── 📄 .gitignore                   # Git ignore
│
├── 🐍 run.py                       # Запуск бота (Python)
├── 🔧 test_db.py                   # Тест базы данных
├── 🔧 start.sh                     # Запуск бота (Bash)
│
├── 📦 medieval_bot/                # Основной пакет
│   │
│   ├── 🐍 __init__.py
│   ├── 🐍 bot.py                   # Точка входа бота
│   ├── 🐍 config.py                # Конфигурация
│   │
│   ├── 📁 database/                # База данных
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 models.py            # SQLAlchemy модели (7 таблиц)
│   │   └── 🐍 engine.py            # Подключение к БД
│   │
│   ├── 📁 handlers/                # Обработчики запросов
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 registration.py     # Регистрация персонажей
│   │   ├── 🐍 profile.py           # Профиль и инвентарь
│   │   ├── 🐍 kingdoms.py          # Навигация по королевству
│   │   ├── 🐍 travel.py            # Путешествия
│   │   ├── 🐍 shop.py              # Магазины
│   │   ├── 🐍 exchange.py          # Обмен валют
│   │   └── 🐍 casino.py            # Казино (6 игр)
│   │
│   ├── 📁 keyboards/               # Клавиатуры
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 inline.py            # InlineKeyboard (15+ штук)
│   │
│   └── 📁 utils/                   # Утилиты
│       ├── 🐍 __init__.py
│       ├── 🐍 currency.py          # Конвертация валют
│       ├── 🐍 game_logic.py        # Логика игр казино
│       └── 🐍 text_generator.py    # Генерация текстов
│
├── 📁 venv/                        # Virtual environment (не в git)
└── 📄 medieval_rpg.db              # SQLite база данных (не в git)
```

## 📊 Statistics

### By Directory

```
📁 Root Level
   ├── Documentation files: 8
   ├── Config files: 2
   ├── Scripts: 3
   └── Total: 13 files

📦 medieval_bot/
   ├── Core files: 3
   ├── Database: 3 files
   ├── Handlers: 8 files
   ├── Keyboards: 2 files
   ├── Utils: 4 files
   └── Total: 20 files

Total project files: 33+ files
```

### By Type

```
🐍 Python files (.py):        20+
📄 Markdown files (.md):      8
⚙️ Config files:              2
🔧 Shell scripts (.sh):       1
📜 Other:                     2

Total: 33+ files
```

## 🗂️ File Descriptions

### Documentation

| Файл | Размер | Описание |
|------|--------|----------|
| `README.md` | 7KB | Основная документация проекта |
| `QUICKSTART.md` | 4.7KB | Инструкция быстрого старта |
| `GAMES.md` | 7.9KB | Подробное описание всех игр казино |
| `DEVELOPMENT.md` | 8.7KB | Руководство для разработчиков |
| `API.md` | 11.8KB | Полное API Reference |
| `PROJECT_STATUS.md` | 8KB | Статус и чеклист проекта |
| `CHANGELOG.md` | 6KB | История версий |
| `STRUCTURE.md` | - | Структура проекта (этот файл) |

### Core Python Files

| Файл | Строк | Описание |
|------|-------|----------|
| `bot.py` | ~60 | Главная точка входа, регистрация роутеров |
| `config.py` | ~20 | Конфигурация (токен, БД, лимиты) |
| `run.py` | ~30 | Скрипт запуска с обработкой ошибок |
| `test_db.py` | ~50 | Тест инициализации базы данных |

### Database Files

| Файл | Строк | Описание |
|------|-------|----------|
| `models.py` | ~120 | 7 моделей SQLAlchemy |
| `engine.py` | ~60 | Async подключение и инициализация |

### Handler Files

| Файл | Строк | Описание |
|------|-------|----------|
| `registration.py` | ~250 | FSM регистрации, выбор расы/класса |
| `profile.py` | ~120 | Профиль, инвентарь, квесты |
| `kingdoms.py` | ~150 | 9 локаций королевства |
| `travel.py` | ~100 | Путешествия между королевствами |
| `shop.py` | ~120 | 5 категорий магазинов |
| `exchange.py` | ~250 | Обмен и размен валют |
| `casino.py` | ~800+ | 6 игр казино со статистикой |

### Utility Files

| Файл | Строк | Описание |
|------|-------|----------|
| `currency.py` | ~60 | Конвертация 4 валют |
| `game_logic.py` | ~200 | Логика всех 6 игр |
| `text_generator.py` | ~80 | Шаблоны и случайные тексты |
| `inline.py` | ~300 | 15+ InlineKeyboard макетов |

## 🎯 Module Dependencies

```
bot.py
  └─ handlers/
      ├─ registration.py
      │   ├─ database/models.py
      │   ├─ database/engine.py
      │   ├─ keyboards/inline.py
      │   └─ utils/text_generator.py
      │
      ├─ profile.py
      │   ├─ database/models.py
      │   ├─ keyboards/inline.py
      │   └─ utils/currency.py
      │
      ├─ kingdoms.py
      │   ├─ database/models.py
      │   ├─ keyboards/inline.py
      │   └─ utils/text_generator.py
      │
      ├─ travel.py
      │   ├─ database/models.py
      │   ├─ keyboards/inline.py
      │   └─ utils/currency.py
      │
      ├─ shop.py
      │   ├─ database/models.py
      │   ├─ keyboards/inline.py
      │   └─ utils/currency.py
      │
      ├─ exchange.py
      │   ├─ database/models.py
      │   ├─ keyboards/inline.py
      │   └─ utils/currency.py
      │
      └─ casino.py
          ├─ database/models.py
          ├─ keyboards/inline.py
          ├─ utils/currency.py
          ├─ utils/game_logic.py
          └─ utils/text_generator.py
```

## 💾 Database Schema

```
medieval_rpg.db (SQLite)
│
├── 📊 users
│   ├── user_id (PK)
│   ├── username
│   ├── character_name (unique)
│   ├── race
│   ├── character_class
│   ├── kingdom
│   ├── level
│   ├── experience
│   ├── copper_coins (все валюты в меди!)
│   ├── registration_date
│   ├── last_daily_bonus
│   └── current_location
│
├── 📊 stats
│   ├── id (PK)
│   ├── user_id (FK → users)
│   ├── strength
│   ├── agility
│   ├── intelligence
│   ├── endurance
│   ├── luck
│   ├── health / max_health
│   ├── mana / max_mana
│   └── energy / max_energy
│
├── 📊 inventory
│   ├── item_id (PK)
│   ├── user_id (FK → users)
│   ├── item_type
│   ├── item_name
│   ├── quantity
│   ├── equipped
│   └── item_data (JSON)
│
├── 📊 kingdoms
│   ├── kingdom_id (PK)
│   ├── kingdom_name (unique)
│   ├── race (unique)
│   ├── population
│   └── description
│
├── 📊 shops
│   ├── shop_id (PK)
│   ├── kingdom_name
│   ├── shop_type
│   ├── item_name
│   ├── item_description
│   ├── price_copper
│   └── item_data (JSON)
│
├── 📊 casino_stats
│   ├── id (PK)
│   ├── user_id (FK → users, unique)
│   ├── games_played
│   ├── total_won (в меди)
│   ├── total_lost (в меди)
│   ├── biggest_win (в меди)
│   ├── lucky_streak
│   ├── current_streak
│   └── last_game_time
│
└── 📊 achievements
    ├── achievement_id (PK)
    ├── user_id (FK → users)
    ├── achievement_name
    ├── achievement_description
    └── unlocked_date
```

## 🎮 Game Flow

```
START
  │
  ├─→ /start
  │     │
  │     ├─→ [Registered?]
  │     │      ├─ Yes → Main Menu
  │     │      └─ No → Registration Flow
  │     │
  │     └─→ Registration:
  │           1. Enter name
  │           2. Select race (→ sets kingdom)
  │           3. Select class
  │           4. Calculate stats
  │           5. Get 500 copper coins
  │           └─→ Main Menu
  │
  └─→ Main Menu
        │
        ├─→ 🏰 Kingdom
        │     ├─ 🏛️ Square
        │     ├─ 👑 Throne
        │     ├─ 🏪 Market
        │     ├─ ⚔️ Arena
        │     ├─ 🏡 Tavern
        │     ├─ 🔧 Forge
        │     ├─ 📚 Library
        │     ├─ 💱 Exchange
        │     │     ├─ Exchange up (copper→silver→gold→platinum)
        │     │     ├─ Exchange down (platinum→gold→silver→copper)
        │     │     └─ View rates
        │     └─ 🎲 Casino
        │
        ├─→ 👤 Profile
        │     ├─ View stats
        │     ├─ View wallet
        │     └─ Casino statistics
        │
        ├─→ 🎒 Inventory (placeholder)
        │
        ├─→ 🗺️ Travel
        │     ├─ Валхейм (⚪ 10 silver)
        │     ├─ Сильвания (⚪ 15 silver)
        │     ├─ Казад-Дум (⚪ 20 silver)
        │     └─ Кхан-Гор (⚪ 25 silver)
        │
        ├─→ ⚔️ Quests (placeholder)
        │
        ├─→ 🏪 Shop
        │     ├─ ⚔️ Weapons
        │     ├─ 🛡️ Armor
        │     ├─ 🧪 Potions
        │     ├─ 📜 Magic
        │     └─ 🍖 Food
        │
        ├─→ ⚒️ Craft (placeholder)
        │
        └─→ 🎲 Casino
              ├─ Select currency (copper/silver/gold/platinum)
              ├─ Select game:
              │   ├─ 🎯 Axe Throwing (luck-based)
              │   ├─ 🎲 Dice of Fate (3 dice)
              │   ├─ 🃏 Knight's Poker (vs bot)
              │   ├─ 🏹 Target Shooting (agility-based)
              │   ├─ ⚔️ Gladiator Roulette (color/zero)
              │   └─ 🔮 Rune Divination (3 runes)
              ├─ Place bet
              ├─ Play game
              ├─ View result
              │   ├─ Win → +coins, +stats
              │   └─ Lose → -coins, reset streak
              └─ Play again / Change bet / Back
```

## 📦 Deployment Files

```
Production Deployment:
├── medieval_rpg.db          # Database file
├── venv/                    # Virtual environment
├── medieval_bot/            # Source code
├── requirements.txt         # Dependencies
└── run.py or start.sh      # Startup script

Environment Variables (optional):
├── BOT_TOKEN               # Telegram bot token
├── DATABASE_URL            # Database connection string
└── REDIS_URL              # Redis connection (optional)
```

## 🔄 Data Flow

```
User Action (Telegram)
    ↓
aiogram Handler
    ↓
FSM State (if needed)
    ↓
Database Query (async)
    ↓
Business Logic
    ↓
Update Database
    ↓
Format Response
    ↓
Send to User (Telegram)
```

## 🎨 Code Organization Principles

1. **Separation of Concerns**
   - Handlers: User interaction
   - Models: Database structure
   - Utils: Reusable logic
   - Keyboards: UI layouts

2. **Async/Await**
   - All I/O operations are async
   - Non-blocking database queries
   - Efficient handling of multiple users

3. **FSM Pattern**
   - Multi-step processes use FSM
   - State data stored in memory
   - Clean user flow

4. **DRY (Don't Repeat Yourself)**
   - Currency conversion in utils
   - Game logic centralized
   - Keyboard layouts reusable

---

**Структура продумана для масштабирования! 🚀**
