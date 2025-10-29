#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы базы данных
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from medieval_bot.database.engine import init_db, async_session_maker
from medieval_bot.database.models import User, Stats, Kingdom
from sqlalchemy import select

async def test_database():
    """Тест базы данных"""
    print("🔧 Инициализация базы данных...")
    await init_db()
    print("✅ База данных инициализирована!")
    
    print("\n📊 Проверка королевств...")
    async with async_session_maker() as session:
        result = await session.execute(select(Kingdom))
        kingdoms = result.scalars().all()
        
        if kingdoms:
            print(f"✅ Найдено королевств: {len(kingdoms)}")
            for kingdom in kingdoms:
                print(f"   🏰 {kingdom.kingdom_name} ({kingdom.race})")
        else:
            print("❌ Королевства не найдены!")
            return False
    
    print("\n✅ Все проверки пройдены!")
    print("\n📁 Файл базы данных создан: medieval_rpg.db")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🏰 Medieval RPG Bot - Database Test")
    print("=" * 50)
    print()
    
    try:
        result = asyncio.run(test_database())
        if result:
            print("\n🎉 База данных готова к работе!")
            sys.exit(0)
        else:
            print("\n❌ Тест не пройден!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
