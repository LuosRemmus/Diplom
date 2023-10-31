from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.config import DATABASE_URL

"""
Вот тут по хорошему надо сделать метод setup_database, который уже будет возвращать engine и\\или sessionmaker

А зависимостями уже управлять на уровне fastapi там, где они нужны будут
"""

engine: AsyncEngine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
