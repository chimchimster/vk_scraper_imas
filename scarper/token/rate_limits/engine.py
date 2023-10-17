import sqlite3

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import OperationalError

from .models import Base


class EngineSQLite3:
    db_url = "sqlite+aiosqlite:///states.db"
    engine = create_async_engine(db_url)

    async def create_db_if_not_exists(self):
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except OperationalError:
            pass


engine_sqlite3 = EngineSQLite3()
