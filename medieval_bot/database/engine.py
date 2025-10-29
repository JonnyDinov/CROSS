from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from medieval_bot.database.models import Base, Kingdom
from medieval_bot.config import config

engine = create_async_engine(config.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await init_kingdoms()

async def init_kingdoms():
    """Инициализация королевств"""
    from sqlalchemy import select
    
    kingdoms_data = [
        {
            'kingdom_name': 'Валхейм',
            'race': 'Люди',
            'description': 'Королевство Валхейм - центр человеческой цивилизации. Плодородные земли, развитая торговля, рыцарские ордены.'
        },
        {
            'kingdom_name': 'Сильвания',
            'race': 'Эльфы',
            'description': 'Лесное Царство Сильвания - древние леса эльфов. Магические источники, луки и магия.'
        },
        {
            'kingdom_name': 'Казад-Дум',
            'race': 'Дварфы',
            'description': 'Подгорное Королевство Казад-Дум - горные залы дварфов. Кузницы, шахты с рудой.'
        },
        {
            'kingdom_name': 'Кхан-Гор',
            'race': 'Орки',
            'description': 'Степные Земли Кхан-Гор - суровые степи орков. Военные лагеря, культ силы.'
        }
    ]
    
    async with async_session_maker() as session:
        for kingdom_data in kingdoms_data:
            result = await session.execute(
                select(Kingdom).where(Kingdom.kingdom_name == kingdom_data['kingdom_name'])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                kingdom = Kingdom(**kingdom_data)
                session.add(kingdom)
        
        await session.commit()

async def get_session() -> AsyncSession:
    """Получить сессию базы данных"""
    async with async_session_maker() as session:
        yield session
