from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    """Главное меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏰 Королевство", callback_data="kingdom")],
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
            InlineKeyboardButton(text="🎒 Инвентарь", callback_data="inventory")
        ],
        [
            InlineKeyboardButton(text="🗺️ Путешествия", callback_data="travel"),
            InlineKeyboardButton(text="⚔️ Квесты", callback_data="quests")
        ],
        [
            InlineKeyboardButton(text="🏪 Магазин", callback_data="shop"),
            InlineKeyboardButton(text="⚒️ Крафт", callback_data="craft")
        ],
        [InlineKeyboardButton(text="🎲 Зал Удачи", callback_data="casino_main")]
    ])
    return keyboard

def kingdom_menu_keyboard():
    """Меню королевства"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏛️ Центральная площадь", callback_data="kingdom_square")],
        [InlineKeyboardButton(text="👑 Тронный зал", callback_data="kingdom_throne")],
        [InlineKeyboardButton(text="🏪 Торговая улица", callback_data="kingdom_market")],
        [InlineKeyboardButton(text="⚔️ Арена", callback_data="kingdom_arena")],
        [InlineKeyboardButton(text="🏡 Таверна", callback_data="kingdom_tavern")],
        [InlineKeyboardButton(text="🔧 Кузница", callback_data="kingdom_forge")],
        [InlineKeyboardButton(text="📚 Библиотека", callback_data="kingdom_library")],
        [InlineKeyboardButton(text="💱 Обменная лавка", callback_data="exchange")],
        [InlineKeyboardButton(text="🎲 Зал Удачи", callback_data="casino_main")],
        [InlineKeyboardButton(text="⬅️ Назад в главное меню", callback_data="main_menu")]
    ])
    return keyboard

def race_selection_keyboard():
    """Выбор расы"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Люди", callback_data="race_Люди")],
        [InlineKeyboardButton(text="🧝 Эльфы", callback_data="race_Эльфы")],
        [InlineKeyboardButton(text="⚒️ Дварфы", callback_data="race_Дварфы")],
        [InlineKeyboardButton(text="💪 Орки", callback_data="race_Орки")]
    ])
    return keyboard

def class_selection_keyboard():
    """Выбор класса"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Воин", callback_data="class_Воин")],
        [InlineKeyboardButton(text="🔮 Маг", callback_data="class_Маг")],
        [InlineKeyboardButton(text="🏹 Лучник", callback_data="class_Лучник")],
        [InlineKeyboardButton(text="✨ Жрец", callback_data="class_Жрец")]
    ])
    return keyboard

def casino_main_keyboard():
    """Главное меню казино"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Метание топоров", callback_data="casino_axe")],
        [InlineKeyboardButton(text="🎲 Кости Судьбы", callback_data="casino_dice")],
        [InlineKeyboardButton(text="🃏 Рыцарский покер", callback_data="casino_poker")],
        [InlineKeyboardButton(text="🏹 Стрельба по мишеням", callback_data="casino_shooting")],
        [InlineKeyboardButton(text="⚔️ Гладиаторская рулетка", callback_data="casino_roulette")],
        [InlineKeyboardButton(text="🔮 Гадание на рунах", callback_data="casino_runes")],
        [InlineKeyboardButton(text="💰 Выбрать валюту ставки", callback_data="casino_currency")],
        [InlineKeyboardButton(text="📜 Правила игр", callback_data="casino_rules")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])
    return keyboard

def currency_selection_keyboard():
    """Выбор валюты для ставки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟤 Медный стол (1-99 мед.)", callback_data="currency_copper")],
        [InlineKeyboardButton(text="⚪ Серебряный стол (1-99 сер.)", callback_data="currency_silver")],
        [InlineKeyboardButton(text="🟡 Золотой стол (1-99 зол.)", callback_data="currency_gold")],
        [InlineKeyboardButton(text="💎 Платиновый стол (1-10 плат.)", callback_data="currency_platinum")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="casino_main")]
    ])
    return keyboard

def exchange_menu_keyboard():
    """Меню обмена валют"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬆️ Обменять на более ценную", callback_data="exchange_up")],
        [InlineKeyboardButton(text="⬇️ Разменять на мелочь", callback_data="exchange_down")],
        [InlineKeyboardButton(text="📊 Курс обмена", callback_data="exchange_rates")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="kingdom")]
    ])
    return keyboard

def exchange_up_keyboard():
    """Обмен на более ценную валюту"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟤➡️⚪ Медь → Серебро", callback_data="exchange_copper_silver")],
        [InlineKeyboardButton(text="⚪➡️🟡 Серебро → Золото", callback_data="exchange_silver_gold")],
        [InlineKeyboardButton(text="🟡➡️💎 Золото → Платина", callback_data="exchange_gold_platinum")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="exchange")]
    ])
    return keyboard

def exchange_down_keyboard():
    """Размен на мелочь"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎➡️🟡 Платина → Золото", callback_data="exchange_platinum_gold")],
        [InlineKeyboardButton(text="🟡➡️⚪ Золото → Серебро", callback_data="exchange_gold_silver")],
        [InlineKeyboardButton(text="⚪➡️🟤 Серебро → Медь", callback_data="exchange_silver_copper")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="exchange")]
    ])
    return keyboard

def travel_menu_keyboard(current_kingdom: str):
    """Меню путешествий"""
    kingdoms = [
        ("🏰 Валхейм", "travel_Валхейм", 10),
        ("🌲 Сильвания", "travel_Сильвания", 15),
        ("⛰️ Казад-Дум", "travel_Казад-Дум", 20),
        ("⚔️ Кхан-Гор", "travel_Кхан-Гор", 25)
    ]
    
    buttons = []
    for name, callback, cost in kingdoms:
        kingdom_name = name.split()[1]
        if kingdom_name != current_kingdom:
            buttons.append([InlineKeyboardButton(
                text=f"{name} (⚪ {cost} сер.)",
                callback_data=callback
            )])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def shop_menu_keyboard():
    """Меню магазинов"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Оружейная лавка", callback_data="shop_weapons")],
        [InlineKeyboardButton(text="🛡️ Доспехи и броня", callback_data="shop_armor")],
        [InlineKeyboardButton(text="🧪 Алхимическая лавка", callback_data="shop_potions")],
        [InlineKeyboardButton(text="📜 Магическая гильдия", callback_data="shop_magic")],
        [InlineKeyboardButton(text="🍖 Провиант", callback_data="shop_food")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])
    return keyboard

def back_to_casino_keyboard():
    """Кнопка возврата в казино"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Играть ещё раз", callback_data="casino_play_again")],
        [InlineKeyboardButton(text="💰 Изменить ставку", callback_data="casino_change_bet")],
        [InlineKeyboardButton(text="⬅️ Назад в казино", callback_data="casino_main")]
    ])
    return keyboard

def game_action_keyboard(game_type: str):
    """Кнопки действий для игр"""
    keyboards = {
        'axe': [
            [InlineKeyboardButton(text="🎯 Бросить топор!", callback_data="play_axe_throw")]
        ],
        'dice': [
            [InlineKeyboardButton(text="🎲 Бросить кости!", callback_data="play_dice_roll")]
        ],
        'poker': [
            [InlineKeyboardButton(text="🃏 Раздать карты!", callback_data="play_poker_deal")]
        ],
        'shooting': [
            [InlineKeyboardButton(text="🏹 Начать стрельбу!", callback_data="play_shooting_start")]
        ],
        'roulette': [
            [InlineKeyboardButton(text="🔴 Красный", callback_data="roulette_red")],
            [InlineKeyboardButton(text="🔵 Синий", callback_data="roulette_blue")],
            [InlineKeyboardButton(text="⚫ Ноль (0)", callback_data="roulette_zero")]
        ],
        'runes': [
            [InlineKeyboardButton(text="🔮 Начать гадание", callback_data="play_runes_divine")]
        ]
    }
    
    buttons = keyboards.get(game_type, [])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад в казино", callback_data="casino_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
