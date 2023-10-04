import sys
from functools import wraps

from session import AsyncSessionLocal


def execute_transaction(coro):
    @wraps(coro)
    async def wrapper(*args, **kwargs):

        async with AsyncSessionLocal() as session:
            async with session.begin() as transaction:

                try:
                    return await coro(*args, **kwargs, session=session)
                except Exception as e:
                    await transaction.rollback()
                    sys.stderr.write(str(e))
                finally:
                    await transaction.commit()

    return wrapper

