import asyncio
import json
import time
from typing import List, Tuple, Dict, Union

from sqlalchemy import select, update, insert, join, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *
from .common import *
from vk_scraper_imas.utils import generate_hash, generate_event
from .decorators import execute_transaction


@execute_transaction
async def get_source_ids(offset: int, limit: int, source_type: int = 1, **kwargs) -> List[Tuple]:
    """ Получение уникальных идентификаторов соцсети Вконтакте пользователей. """

    session = kwargs.get('session')

    stmt = select(Source.source_id).where(Source.source_type == source_type).order_by(Source.res_id).offset(
        offset).limit(limit)

    chunked_iterator_result = await session.execute(stmt)

    ids = chunked_iterator_result.fetchall()

    return ids


@execute_transaction
async def get_source_ids_count(source_type: int = 1, **kwargs) -> int:
    """ Получение общего количества доступных source_id.
        :source_id: идентификатор пользовтеля/группы Вконтакте. """

    session = kwargs.get('session')

    stmt = select(func.count(Source.source_id)).select_from(Source).where(Source.source_type == source_type)

    count = await session.execute(stmt)

    return count.scalar() or 0


@execute_transaction
async def user_handler(user_profile: Dict, **kwargs):
    """ Добавление данных о пользователе Вконтакте. """

    session = kwargs.get('session')

    to_relational_fields_mapped, json_field, source_id = await prepare_data(
        user_profile,
        flag='user',
    )

    res_id = await get_user_res_id(source_id, session)

    if res_id:
        user_exists = await check_if_user_exists(res_id, session)
        if not user_exists:
            await insert_user_into_source_user_profile(res_id, to_relational_fields_mapped, json_field, session)
            # ВОТ ТУТ НУЖНО ОБРАБОТАТЬ ВАРИАНТ С LAST_SEEN И FOLLOWERS COUNT - они не хэшируются, но и ивент по ним не записывается!
            await insert_hash_into_scrapper_hash(res_id, to_relational_fields_mapped + json.dumps(json_field), session)
            await insert_event_into_source_user_event(res_id, to_relational_fields_mapped + json.dumps(json_field), session)


async def get_user_res_id(user_source_id: int, session: AsyncSession) -> Union[int, None]:
    stmt = select(Source.res_id).filter_by(source_id=user_source_id)
    result = await session.execute(stmt)

    if result:
        return result.scalar()
    return None


async def check_if_user_exists(user_res_id: int, session: AsyncSession) -> bool:
    stmt = select(UserProfile).filter_by(res_id=user_res_id)
    result = await session.execute(stmt)

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

    now = time.time()
    map_events = [
       {'event_time': now, 'res_id': user_res_id, 'event_type': key, 'event_value': value} for key, value in data.items()
    ]

    stmt = insert(UserEvent).values(map_events)
    await session.execute(stmt)


@execute_transaction
async def subscription_handler(user_subscription: Dict, user_source_id: int, **kwargs):
    session = kwargs.pop('session')

    to_relational_fields_mapped, json_field, subscription_source_id = await prepare_data(
        user_subscription,
        flag='subscription',
    )

    subscription_exists = await check_if_subscription_exists(subscription_source_id, session)

    user_res_id = await get_vk_user_res_id(user_source_id, session)

    if not subscription_exists:

        await insert_subscription_into_source(subscription_source_id, session)

        subscription_res_id = await get_vk_subscription_res_id(subscription_source_id, session)

        if user_res_id and subscription_res_id:
            await create_connection_between_user_and_subscription(user_res_id, subscription_res_id, session)

            await insert_subscription_into_source_subscription_profile(
                subscription_res_id, to_relational_fields_mapped, json_field, session
            )
    else:

        subscription_res_id = await get_vk_subscription_res_id(subscription_source_id, session)

        has_connection = await check_if_connection_between_user_and_subscription_exists(
            user_res_id, subscription_res_id, session
        )

        if not has_connection:
            await create_connection_between_user_and_subscription(user_res_id, subscription_res_id, session)


async def get_vk_user_res_id(user_source_id: int, session: AsyncSession) -> Union[int, None]:
    user_profile = select(Source.res_id).filter_by(source_id=user_source_id)
    user_profile = await session.execute(user_profile)

    if user_profile:
        return user_profile.scalar()
    return None


async def get_vk_subscription_res_id(subscription_source_id: int, session: AsyncSession) -> Union[int, None]:
    stmt = select(Source.res_id).filter_by(source_id=subscription_source_id)
    result = await session.execute(stmt)

    if result:
        return result.scalar()
    return None


async def create_connection_between_user_and_subscription(
        user_res_id: int,
        subscription_res_id: int,
        session: AsyncSession,
) -> None:
    stmt = insert(UserSubscription).values(
        user_res_id=user_res_id,
        subscription_res_id=subscription_res_id,
        status=1,
    )

    await session.execute(stmt)


async def check_if_subscription_exists(subscription_source_id: int, session: AsyncSession) -> bool:
    """ Проверка на наличия группы по source_id """

    stmt = select(Source.res_id).filter_by(source_id=subscription_source_id)

    result = await session.execute(stmt)

    if not result:
        return False
    return True


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
