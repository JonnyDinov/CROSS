from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    character_name = Column(String(255), unique=True, nullable=False)
    race = Column(String(50), nullable=False)
    character_class = Column(String(50), nullable=False)
    kingdom = Column(String(100), nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    copper_coins = Column(BigInteger, default=500)
    registration_date = Column(DateTime, default=func.now())
    last_daily_bonus = Column(DateTime, nullable=True)
    current_location = Column(String(100), nullable=True)

class Stats(Base):
    __tablename__ = 'stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), unique=True)
    strength = Column(Integer, default=10)
    agility = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    endurance = Column(Integer, default=10)
    luck = Column(Integer, default=10)
    health = Column(Integer, default=100)
    max_health = Column(Integer, default=100)
    mana = Column(Integer, default=50)
    max_mana = Column(Integer, default=50)
    energy = Column(Integer, default=100)
    max_energy = Column(Integer, default=100)

class Inventory(Base):
    __tablename__ = 'inventory'
    
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    item_type = Column(String(50))
    item_name = Column(String(255))
    quantity = Column(Integer, default=1)
    equipped = Column(Boolean, default=False)
    item_data = Column(Text, nullable=True)

class Kingdom(Base):
    __tablename__ = 'kingdoms'
    
    kingdom_id = Column(Integer, primary_key=True, autoincrement=True)
    kingdom_name = Column(String(100), unique=True)
    race = Column(String(50), unique=True)
    population = Column(Integer, default=0)
    description = Column(Text)

class Shop(Base):
    __tablename__ = 'shops'
    
    shop_id = Column(Integer, primary_key=True, autoincrement=True)
    kingdom_name = Column(String(100))
    shop_type = Column(String(50))
    item_name = Column(String(255))
    item_description = Column(Text)
    price_copper = Column(BigInteger)
    item_data = Column(Text, nullable=True)

class CasinoStats(Base):
    __tablename__ = 'casino_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), unique=True)
    games_played = Column(Integer, default=0)
    total_won = Column(BigInteger, default=0)
    total_lost = Column(BigInteger, default=0)
    biggest_win = Column(BigInteger, default=0)
    lucky_streak = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    last_game_time = Column(DateTime, nullable=True)

class Achievement(Base):
    __tablename__ = 'achievements'
    
    achievement_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    achievement_name = Column(String(255))
    achievement_description = Column(Text)
    unlocked_date = Column(DateTime, default=func.now())
