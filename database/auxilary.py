import time

from datetime import datetime
from typing import Dict, Union

from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *
from .common import *
from vk_scraper_imas.utils import *


async def get_vk_user_res_id(
        user_source_id: int,
        session: AsyncSession,
        source_type: int = 1,
) -> Union[int, None]:
    """ Получение системного идентификатора пользователя. """

    stmt = select(Source.res_id).filter_by(source_id=user_source_id, source_type=source_type)
    result = await session.execute(stmt)
    result = result.scalar()

    if result:
        return result
    return None


async def get_vk_subscription_res_id(
        subscription_source_id: int,
        session: AsyncSession,
        source_type: int = 2,
) -> Union[int, None]:
    """ Получение системного идентификатора подписки. """

    stmt = select(Source.res_id).filter_by(source_id=subscription_source_id, source_type=source_type)
    result = await session.execute(stmt)
    result = result.scalar()

    if result:
        return result
    return None


async def create_connection_between_user_and_subscription(
        user_res_id: int,
        subscription_res_id: int,
        session: AsyncSession,
) -> None:
    """ Создание связи многие ко многим для пользователя и подписки. """

    stmt = insert(UserSubscription).values(
        user_res_id=user_res_id,
        subscription_res_id=subscription_res_id,
        status=1,
    )

    await session.execute(stmt)


async def check_if_subscription_exists(subscription_source_id: int, session: AsyncSession) -> bool:
    """ Проверка на наличия группы по API айди Вконтакте. """

    stmt = select(Source.res_id).filter_by(source_id=subscription_source_id)
    result = await session.execute(stmt)
    result = result.scalar()

    if result:
        return True
    return False


async def check_if_connection_between_user_and_subscription_exists(
        user_res_id: int,
        subscription_res_id: int,
        session: AsyncSession,
) -> bool:
    """ Проверка наличия связи между пользователем и группой. """

    stmt = select(UserSubscription).filter_by(
        user_res_id=user_res_id,
        subscription_res_id=subscription_res_id,
    )

    result = await session.execute(stmt)

    if not result:
        return False
    return True


async def insert_subscription_into_source_subscription_profile(
        subscription_res_id: int,
        to_relational_fields_mapped: Dict,
        json_field: str,
        session: AsyncSession,
) -> None:

    stmt = insert(SubscriptionProfile).values(
        res_id=subscription_res_id,
        **to_relational_fields_mapped,
        info_json=json_field,
    )

    await session.execute(stmt)


async def insert_subscription_into_source(subscription_source_id: int, session: AsyncSession) -> None:

    stmt = insert(Source).values(
        soc_type=1,
        source_id=subscription_source_id,
        source_type=2,
    )

    await session.execute(stmt)


async def get_user_hash(user_res_id: int, session: AsyncSession) -> Union[str, None]:

    stmt = select(ScrapperHash.social_info_hash).filter_by(res_id=user_res_id)
    result = await session.execute(stmt)
    result = result.scalar()

    if result:
        return result
    return None


async def update_user_hash(user_res_id: int, data_to_hash: Dict, session: AsyncSession) -> None:

    new_hash = await generate_hash(data_to_hash)

    stmt = update(ScrapperHash).filter_by(res_id=user_res_id).values(social_info_hash=new_hash)
    await session.execute(stmt)


async def update_user_in_source_user_profile(
        user_res_id: int,
        to_relational_fields_mapped: Dict,
        json_field: str,
        session: AsyncSession
) -> None:

    stmt = update(UserProfile).filter_by(res_id=user_res_id).values(**to_relational_fields_mapped, info_json=json_field)
    await session.execute(stmt)


async def get_user_res_id(user_source_id: int, session: AsyncSession) -> Union[int, None]:

    stmt = select(Source.res_id).filter_by(source_id=user_source_id)
    result = await session.execute(stmt)
    result = result.scalar()

    if result:
        return result
    return None


async def check_if_user_exists(user_res_id: int, session: AsyncSession) -> bool:

    stmt = select(UserProfile).filter_by(res_id=user_res_id)
    result = await session.execute(stmt)
    result = result.scalar()

    if result:
        return True
    return False


async def insert_user_into_source_user_profile(
        user_res_id: int,
        to_relational_fields_mapped: Dict,
        json_field: str,
        session: AsyncSession,
) -> None:

    stmt = insert(UserProfile).values(
       res_id=user_res_id,
       **to_relational_fields_mapped,
       info_json=json_field,
    )

    await session.execute(stmt)


async def insert_hash_into_scrapper_hash(
        user_res_id: int,
        hash_data: Dict,
        session: AsyncSession,
) -> None:

    generated_hash = await generate_hash(hash_data)

    stmt = insert(ScrapperHash).values(res_id=user_res_id, social_info_hash=generated_hash)
    await session.execute(stmt)


async def insert_event_into_source_user_event(
        user_res_id: int,
        data: Dict,
        session: AsyncSession,
) -> None:

    flatten_dict = await flat_dict(data)

    now = int(time.time())
    map_events = [
       {
           'event_time': now,
           'res_id': user_res_id,
           'event_type': key,
           'event_value': value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value
       } for key, value in flatten_dict.items()
    ]

    stmt = insert(UserEvent).values(map_events)
    await session.execute(stmt)


__all__ = [
    'insert_event_into_source_user_event',
    'insert_hash_into_scrapper_hash',
    'insert_user_into_source_user_profile',
    'check_if_user_exists',
    'get_user_res_id',
    'update_user_in_source_user_profile',
    'update_user_hash',
    'get_user_hash',
    'insert_subscription_into_source',
    'insert_subscription_into_source_subscription_profile',
    'check_if_connection_between_user_and_subscription_exists',
    'check_if_subscription_exists',
    'create_connection_between_user_and_subscription',
    'get_vk_subscription_res_id',
    'get_vk_user_res_id',
]
