import sys
import asyncio
import aiosqlite
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from engine import engine_sqlite3
from models import Token, VKObject, State


AsyncSessionLocal = sessionmaker(
    engine_sqlite3.engine, class_=AsyncSession, expire_on_commit=False
)


class APIStateDB:

    @staticmethod
    async def insert_new_token(token: str):

        await engine_sqlite3.create_bd_if_not_exists()

        async with AsyncSessionLocal() as session:
            async with session.begin() as transaction:
                try:
                    new_token = Token(token=token)
                    print(new_token)
                    session.add(new_token)
                    await transaction.commit()
                except Exception as e:
                    await transaction.rollback()
                    sys.stderr.write(f'Транзакция завершилась неудачно: {e}')

    @staticmethod
    async def insert_new_vk_object(vk_obj_name: str):

        await engine_sqlite3.create_bd_if_not_exists()

        async with AsyncSessionLocal() as session:
            async with session.begin() as transaction:
                try:
                    new_vk_obj = VKObject(object_name=vk_obj_name)
                    session.add(new_vk_obj)
                    await transaction.commit()
                except Exception as e:
                    await transaction.rollback()
                    sys.stderr.write(f'Транзакция завершилась неудачно: {e}')

    @staticmethod
    async def create_new_state(vk_obj_name: str, token: str):

        await engine_sqlite3.create_bd_if_not_exists()

        async with AsyncSessionLocal() as session:
            async with session.begin() as transaction:
                try:

                    token = await session.execute(select(Token).filter_by(token=token))
                    vk_object = await session.execute(select(VKObject).filter_by(object_name=vk_obj_name))

                    token = token.scalar_one_or_none()
                    vk_object = vk_object.scalar_one_or_none()

                    new_state = State(token_id=token.id, vk_object_id=vk_object.id)
                    session.add(new_state)
                    await transaction.commit()
                except Exception as e:
                    await transaction.rollback()
                    sys.stderr.write(f'Транзакция завершилась неудачно: {e}')


async def main():

    a = APIStateDB()

if __name__ == '__main__':

    asyncio.run(main())