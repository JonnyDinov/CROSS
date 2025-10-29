#!/usr/bin/env python3
"""
Скрипт запуска Medieval RPG Bot
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from medieval_bot.bot import main
import asyncio

if __name__ == "__main__":
    print("=" * 50)
    print("🏰 Medieval RPG Telegram Bot")
    print("=" * 50)
    print("Starting bot...")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nBot stopped by user. Goodbye! 👋")
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
