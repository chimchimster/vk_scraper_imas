import sys
from functools import wraps
from typing import Awaitable, Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from engine import engine_sqlite3

AsyncSessionLocal = sessionmaker(
    engine_sqlite3.engine, class_=AsyncSession, expire_on_commit=False
)


def execute_transaction(insert: bool = False, update: bool = False):
    def outter_wrapper(coro):
        @wraps(coro)
        async def inner_wrapper(*args, **kwargs):

            await engine_sqlite3.create_bd_if_not_exists()

            async with AsyncSessionLocal() as session:
                async with session.begin() as transaction:

                    try:
                        obj = await coro(*args, **kwargs, session=session)
                        if isinstance(type(obj), bool) and not obj:
                            return
                        if insert:
                            session.add(obj)
                        if update:
                            await session.execute(obj)
                        await transaction.commit()
                    except Exception as e:
                        await transaction.rollback()
                        sys.stderr.write(f'Транзакция завершилась неудачно: {e}')

        return inner_wrapper

    return outter_wrapper
