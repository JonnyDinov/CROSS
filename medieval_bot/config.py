import os
from dataclasses import dataclass

@dataclass
class Config:
    BOT_TOKEN: str = "7436582648:AAEv-aNtFsx87M1X0tTyAdlnWU1Smyiswgw"
    DATABASE_URL: str = "sqlite+aiosqlite:///./medieval_rpg.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    STARTING_COPPER: int = 500
    
    COPPER_TO_SILVER: int = 100
    SILVER_TO_GOLD: int = 100
    GOLD_TO_PLATINUM: int = 100
    
    COOLDOWN_CASINO: int = 3
    MAX_BET_COPPER: int = 99
    MAX_BET_SILVER: int = 99
    MAX_BET_GOLD: int = 99
    MAX_BET_PLATINUM: int = 10

config = Config()
