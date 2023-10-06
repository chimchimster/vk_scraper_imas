import asyncio
import json
import time
from datetime import datetime

from typing import List, Tuple, Dict, Set, Union, Sequence, Any

from sqlalchemy import select, func, insert, Row, join, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *
from .common import *
from .auxilary import *
from vk_scraper_imas.utils import *
from .decorators import execute_transaction


@execute_transaction
async def users_handler(users_data: List[Dict], **kwargs) -> None:

    session = kwargs.get('session')

    vk_api_unique_identifiers = await get_unique_identifiers(users_data)

    vk_api_identifiers_exist = await check_if_vk_api_identifiers_exist_in_database(vk_api_unique_identifiers, session)

    vk_api_identifiers_which_are_not_in_database = vk_api_identifiers_exist.get('not_in_database')

    if vk_api_identifiers_which_are_not_in_database:
        await insert_vk_api_identifiers_which_are_not_in_database(
            vk_api_identifiers_which_are_not_in_database,
            session,
        )

    mapped_res_and_source_ids = await get_users_res_ids_and_source_ids(vk_api_unique_identifiers, session)

    users_exist = await check_if_profiles_of_users_exist_in_database(
        {tpl[0] for tpl in mapped_res_and_source_ids}, session
    )

    res_ids_which_are_not_in_database = users_exist.get('not_in_database')

    if res_ids_which_are_not_in_database:
        await insert_user_profiles(users_data, res_ids_which_are_not_in_database, session)
        await insert_user_hashes(users_data, res_ids_which_are_not_in_database, session)
        await insert_events(users_data, res_ids_which_are_not_in_database, session)


async def get_unique_identifiers(data: List[Dict]) -> Set[int]:

    return {dct.get('id') for dct in data}


async def check_if_vk_api_identifiers_exist_in_database(vk_api_identifiers: Set[int], session: AsyncSession) -> Dict:

    stmt = select(Source.source_id).where(and_(Source.source_id.in_(vk_api_identifiers), Source.source_type == 1))
    result = await session.execute(stmt)

    in_database = {data[0] for data in result.fetchall()}
    not_in_database = vk_api_identifiers.difference(in_database)

    return {
        'in_database': in_database,
        'not_in_database': not_in_database,
    }


async def insert_vk_api_identifiers_which_are_not_in_database(vk_api_identifiers: Set, session: AsyncSession) -> Source:

    map_identifiers = [
        {'soc_type': 1, 'source_id': source_id, 'source_type': 1} for source_id in vk_api_identifiers
    ]

    stmt = insert(Source).values(map_identifiers)
    result = await session.execute(stmt)

    return result.scalar()


async def get_users_res_ids_and_source_ids(
        vk_api_identifiers: Set[int],
        session: AsyncSession,
) -> Sequence[Row[Tuple[int, int]]]:
    """ :res_id: Системный идентификатор.
        :source_id: Идентификатор API Вконтакте. """

    stmt = select(Source.res_id, Source.source_id).where(Source.source_id.in_(vk_api_identifiers))
    result = await session.execute(stmt)
    result = result.fetchall()

    return result


async def check_if_profiles_of_users_exist_in_database(res_ids: Set[int], session: AsyncSession) -> Dict:

    stmt = select(UserProfile.res_id).where(UserProfile.res_id.in_(res_ids))
    result = await session.execute(stmt)

    in_database = {res[0] for res in result.fetchall()}
    not_in_database = res_ids.difference(in_database)

    return {
        'in_database': in_database,
        'not_in_database': not_in_database
    }


async def insert_user_profiles(
        users_data: List[Dict],
        res_ids: Set[int],
        session: AsyncSession,
) -> None:

    select_stmt = select(Source.res_id, Source.source_id).where(Source.res_id.in_(res_ids))

    res_id_mapping = await session.execute(select_stmt)
    res_id_mapping = {row[1]: row[0] for row in res_id_mapping.fetchall()}

    users_profiles_to_insert = []
    for user_data in users_data:
        source_id = user_data.get('id')
        res_id = res_id_mapping.get(source_id)
        to_relational_fields, to_json_field = await prepare_data(user_data, flag='user')

        if res_id is not None:
            user_profile = {
                'res_id': res_id,
                'info_json': to_json_field
            }

            to_relational_fields.pop('id')
            user_profile.update(to_relational_fields)
            users_profiles_to_insert.append(user_profile)

    if users_profiles_to_insert:
        insert_stmt = insert(UserProfile).values(users_profiles_to_insert)
        await session.execute(insert_stmt)


async def insert_user_hashes(users_data: List[Dict], res_ids: Set[int], session: AsyncSession) -> None:

    select_stmt = select(Source.res_id, Source.source_id).where(Source.res_id.in_(res_ids))

    res_id_mapping = await session.execute(select_stmt)

    res_id_mapping = {row[1]: row[0] for row in res_id_mapping.fetchall()}

    map_res_ids_and_hashes = []
    for user_data in users_data:
        source_id = user_data.get('id')
        res_id = res_id_mapping.get(source_id)
        to_relational_fields, json_field = await prepare_data(user_data, flag='user')
        to_relational_fields.pop('id')
        if res_id is not None:
            prepared_data = {}
            prepared_data.update(to_relational_fields)
            prepared_data.update((json.loads(json_field)))
            map_res_ids_and_hashes.append((res_id, prepared_data))

    tasks = [
        asyncio.create_task(
            generate_hash(*res_id_and_hash)
        ) for res_id_and_hash in map_res_ids_and_hashes
    ]

    generated_hashes = await asyncio.gather(*tasks)

    users_hashes_to_insert = [
        {
            'res_id': generated_hash[0],
            'social_info_hash': generated_hash[1]
        } for generated_hash in generated_hashes
    ]

    insert_stmt = insert(ScrapperHash).values(users_hashes_to_insert)

    await session.execute(insert_stmt)


async def insert_events(users_data: List[Dict], res_ids: Set[int], session: AsyncSession) -> None:

    select_stmt = select(Source.res_id, Source.source_id).where(Source.res_id.in_(res_ids))
    res_id_mapping = await session.execute(select_stmt)

    res_id_mapping = {row[1]: row[0] for row in res_id_mapping.fetchall()}

    map_events = []
    for user_data in users_data:
        source_id = user_data.get('id')
        res_id = res_id_mapping.get(source_id)

        flatten_dict = await flat_dict(user_data)
        now = int(time.time())
        events = [
            {
                'event_time': now,
                'res_id': res_id,
                'event_type': key,
                'event_value': value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value
            } for key, value in flatten_dict.items()
        ]
        map_events.extend(events)

    insert_stmt = insert(UserEvent).values(map_events)
    await session.execute(insert_stmt)


@execute_transaction
async def user_handler(user_profile: Dict, **kwargs) -> None:
    """ Добавление данных о пользователе Вконтакте. """

    session = kwargs.get('session')

    to_relational_fields_mapped, json_field, source_id = await prepare_data(
        user_profile,
        flag='user',
    )

    res_id = await get_user_res_id(source_id, session)

    data_to_hash = {}

    data_to_hash.update(to_relational_fields_mapped)
    data_to_hash.update(json.loads(json_field))

    data_to_event = data_to_hash

    if res_id:
        user_exists = await check_if_user_exists(res_id, session)

        if not user_exists:
            await insert_user_into_source_user_profile(res_id, to_relational_fields_mapped, json_field, session)
            await insert_hash_into_scrapper_hash(res_id, data_to_hash, session)
            await insert_event_into_source_user_event(res_id, data_to_event, session)
        else:
            has_hash = await get_user_hash(res_id, session)

            if has_hash:
                hash_has_been_changed = await validate_hash(has_hash, data_to_hash)

                if not hash_has_been_changed:
                    return

                await update_user_hash(res_id, data_to_hash, session)

                await insert_event_into_source_user_event(res_id, data_to_event, session)
                await update_user_in_source_user_profile(res_id, to_relational_fields_mapped, json_field, session)


@execute_transaction
async def subscription_handler(user_subscription: Dict, user_source_id: int, **kwargs) -> None:
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