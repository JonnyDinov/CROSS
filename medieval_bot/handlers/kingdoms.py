from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from medieval_bot.database.models import User
from medieval_bot.database.engine import async_session_maker
from medieval_bot.keyboards.inline import kingdom_menu_keyboard
from medieval_bot.utils.text_generator import get_kingdom_description

router = Router()

@router.callback_query(F.data == "kingdom")
async def show_kingdom(callback: CallbackQuery):
    """Отображение меню королевства"""
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.answer("Ошибка: персонаж не найден!", show_alert=True)
            return
    
    kingdom_name = user.current_location or user.kingdom
    description = get_kingdom_description(kingdom_name)
    
    kingdom_text = f"""{description}
━━━━━━━━━━━━━━━━━━━━

Выбери, куда отправиться:"""
    
    await callback.message.edit_text(
        kingdom_text,
        reply_markup=kingdom_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "kingdom_square")
async def kingdom_square(callback: CallbackQuery):
    """Центральная площадь"""
    text = """🏛️ <b>Центральная площадь</b>
━━━━━━━━━━━━━━━━━━━━

Ты стоишь в центре королевства. Вокруг тебя кипит жизнь - торговцы зазывают покупателей, 
гвардейцы патрулируют улицы, а дети играют у фонтана.

На площади ты видишь:
• Доску объявлений с новостями
• Фонтан желаний
• Статую основателя королевства

<i>Дополнительные активности будут добавлены в обновлениях.</i>"""
    
    await callback.message.edit_text(text, reply_markup=kingdom_menu_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "kingdom_throne")
async def kingdom_throne(callback: CallbackQuery):
    """Тронный зал"""
    text = """👑 <b>Тронный зал</b>
━━━━━━━━━━━━━━━━━━━━

Величественный зал, где восседает правитель королевства. Здесь можно получить квесты 
от королевской семьи и узнать о важных событиях в землях.

Стражники внимательно следят за посетителями.

<i>Система квестов от правителя будет добавлена позже.</i>"""
    
    await callback.message.edit_text(text, reply_markup=kingdom_menu_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "kingdom_market")
async def kingdom_market(callback: CallbackQuery):
    """Торговая улица"""
    text = """🏪 <b>Торговая улица</b>
━━━━━━━━━━━━━━━━━━━━

Шумная торговая улица, где можно найти всё - от простого хлеба до редких артефактов.

Доступные лавки:
• ⚔️ Оружейная
• 🛡️ Доспехи
• 🧪 Алхимия
• 📜 Магия
• 🍖 Провиант

Используй кнопку "🏪 Магазин" в главном меню для посещения лавок."""
    
    await callback.message.edit_text(text, reply_markup=kingdom_menu_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "kingdom_arena")
async def kingdom_arena(callback: CallbackQuery):
    """Арена"""
    text = """⚔️ <b>Арена</b>
━━━━━━━━━━━━━━━━━━━━

Грандиозная арена, где воины проверяют свою силу в поединках!

Здесь ты можешь:
• Сразиться с другими игроками (PvP)
• Участвовать в турнирах
• Тренироваться с манекенами
• Завоевать славу и награды

<i>Система боёв будет добавлена в следующих обновлениях.</i>"""
    
    await callback.message.edit_text(text, reply_markup=kingdom_menu_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "kingdom_tavern")
async def kingdom_tavern(callback: CallbackQuery):
    """Таверна"""
    text = """🏡 <b>Таверна "Гарцующий единорог"</b>
━━━━━━━━━━━━━━━━━━━━

Уютная таверна, где можно отдохнуть, послушать байки путешественников и найти попутчиков.

В таверне:
• 🍺 Эль и медовуха
• 🍖 Горячая еда
• 🎵 Менестрель играет на лютне
• 📜 Доска заказов

<i>Система отдыха и восстановления энергии будет добавлена позже.</i>"""
    
    await callback.message.edit_text(text, reply_markup=kingdom_menu_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "kingdom_forge")
async def kingdom_forge(callback: CallbackQuery):
    """Кузница"""
    text = """🔧 <b>Кузница</b>
━━━━━━━━━━━━━━━━━━━━

Жаркая кузня, где опытные мастера куют оружие и доспехи.

Услуги кузнеца:
• ⚒️ Ремонт экипировки
• ✨ Улучшение оружия
• 🔨 Крафт новых предметов
• 💎 Вставка самоцветов

<i>Система крафта и улучшений будет доступна в обновлениях.</i>"""
    
    await callback.message.edit_text(text, reply_markup=kingdom_menu_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "kingdom_library")
async def kingdom_library(callback: CallbackQuery):
    """Библиотека"""
    text = """📚 <b>Королевская библиотека</b>
━━━━━━━━━━━━━━━━━━━━

Величественное хранилище знаний. Полки уставлены древними томами и свитками.

В библиотеке можно:
• 📖 Изучать магические заклинания
• 📜 Читать об истории мира
• 🧙 Получать знания от мудрецов
• ✨ Изучать новые умения

<i>Система обучения и навыков будет добавлена позже.</i>"""
    
    await callback.message.edit_text(text, reply_markup=kingdom_menu_keyboard(), parse_mode="HTML")
    await callback.answer()
