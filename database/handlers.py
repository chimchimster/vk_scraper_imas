import asyncio

from sqlalchemy import select, update, join

from models import *
from decorators import execute_transaction


@execute_transaction
async def check_if_hash_exists(res_id: int, **kwargs) -> bool:
    """ Проверяем существует ли хэш запись в таблице scrapper hash.
        :res_id: идентификатор аккаунта в системе. """

    session = kwargs.get('session')

    stmt = select(ScrapperHash).select_from(
        join(ScrapperHash, Source, ScrapperHash.res_id == Source.res_id)
    ).where(Source.res_id == res_id)

    has_hash = await session.execute(stmt)
    has_hash = has_hash.scalar()

    return has_hash



async def check_if_user_updated_profile(res_id: int) -> bool:
    """ Проверка связанного с профилем пользователя хэша в базе данных. """

    pass

async def main():
    x = await check_if_hash_exists(1)
    print(x)

if __name__ == '__main__':
    asyncio.run(main())
