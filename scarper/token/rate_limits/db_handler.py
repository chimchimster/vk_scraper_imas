import asyncio
import time

from sqlalchemy import select, update
from models import Token, VKObject, State
from decorators import execute_transaction


class APIStateDB:

    @staticmethod
    @execute_transaction(insert=True)
    async def insert_token(token: str, **kwargs):
        session = kwargs.pop('session')

        has_token = await session.execute(select(Token).filter_by(token=token))
        has_token = has_token.scalar()

        if not has_token:
            return Token(token=token)
        return None

    @staticmethod
    @execute_transaction(insert=True)
    async def insert_vk_object(vk_obj_name: str, **kwargs):
        session = kwargs.pop('session')

        has_vk_object = await session.execute(select(VKObject).filter_by(object_name=vk_obj_name))
        has_vk_object = has_vk_object.scalar()

        if not has_vk_object:
            return VKObject(object_name=vk_obj_name)
        return None

    @staticmethod
    @execute_transaction(insert=True)
    async def create_state(vk_obj_name: str, token: str, **kwargs):
        session = kwargs.pop('session')

        token = await session.execute(select(Token).filter_by(token=token))
        vk_object = await session.execute(select(VKObject).filter_by(object_name=vk_obj_name))

        token = token.scalar()
        vk_object = vk_object.scalar()

        if not token or not vk_object:
            return None

        has_state = await session.execute(select(State).filter_by(token_id=token.id, vk_object_id=vk_object.id))
        has_state = has_state.scalar()

        if not has_state:
            return State(token_id=token.id, vk_object_id=vk_object.id)
        return None

    @staticmethod
    @execute_transaction(update=True)
    async def update_state(vk_obj_name: str, token: str, expired=False, **kwargs):
        session = kwargs.pop('session')

        token = await session.execute(select(Token).filter_by(token=token))
        vk_object = await session.execute(select(VKObject).filter_by(object_name=vk_obj_name))

        token = token.scalar()
        vk_object = vk_object.scalar()

        if not token or not vk_object:
            return None

        has_state = await session.execute(select(State).filter_by(token_id=token.id, vk_object_id=vk_object.id))
        has_state = has_state.scalar()

        if not expired and has_state:
            return (update(State)
                    .where(State.vk_object_id == vk_object.id)
                    .where(State.token_id == token.id)
                    .values(
                requests=State.requests + 1,
                last_use_unix=int(time.time())
            ))
        elif has_state:
            return (update(State)
                    .where(State.vk_object_id == vk_object.id)
                    .where(State.token_id == token.id)
                    .values(
                expired=expired,
                expired_at_unix=int(time.time())
            ))
        return None


