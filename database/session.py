from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from engine import engine_mysql


AsyncSessionLocal = sessionmaker(
    engine_mysql.engine, class_=AsyncSession, expire_on_commit=False
)