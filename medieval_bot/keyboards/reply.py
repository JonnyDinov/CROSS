from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardRemove

def main_menu_keyboard():
    """Главное меню с обычными кнопками"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🏰 Королевство"),
                KeyboardButton(text="👤 Профиль")
            ],
            [
                KeyboardButton(text="🗺️ Путешествия"),
                KeyboardButton(text="🎒 Инвентарь")
            ],
            [
                KeyboardButton(text="🏪 Магазин"),
                KeyboardButton(text="⚔️ Квесты")
            ],
            [
                KeyboardButton(text="🎲 Зал Удачи")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел..."
    )
    return keyboard

def remove_keyboard():
    """Удалить клавиатуру"""
    return ReplyKeyboardRemove()
