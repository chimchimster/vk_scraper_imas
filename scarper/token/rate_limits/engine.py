from .models import Base
import aiosqlite
from sqlalchemy.ext.asyncio import create_async_engine


class EngineSQLite3:
    db_url = "sqlite+aiosqlite:///states.db"
    engine = create_async_engine(db_url)

    async def create_bd_if_not_exists(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


engine_sqlite3 = EngineSQLite3()
