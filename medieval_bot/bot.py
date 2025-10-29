import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from medieval_bot.config import config
from medieval_bot.database.engine import init_db
from medieval_bot.handlers import (
    registration,
    menu,
    profile,
    kingdoms,
    travel,
    shop,
    exchange,
    casino
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция запуска бота"""
    logger.info("Starting Medieval RPG Bot...")
    
    await init_db()
    logger.info("Database initialized")
    
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.include_router(registration.router)
    dp.include_router(menu.router)
    dp.include_router(profile.router)
    dp.include_router(kingdoms.router)
    dp.include_router(travel.router)
    dp.include_router(shop.router)
    dp.include_router(exchange.router)
    dp.include_router(casino.router)
    
    logger.info("All routers registered")
    
    try:
        logger.info("Bot is starting polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
