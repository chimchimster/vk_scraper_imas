import json

from typing import List, Tuple, Dict, Set, Union, Sequence, Any

from sqlalchemy import select, func, insert, Row, join
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *
from .common import *
from .auxilary import *
from vk_scraper_imas.utils import *
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


async def users_handler(users_data: List[Dict], **kwargs) -> None:

    session = kwargs.get('session')

    vk_api_unique_identifiers = await get_unique_identifiers(users_data)

    vk_api_identifiers_exist = await check_if_vk_api_identifiers_exist_in_database(vk_api_unique_identifiers, session)

    not_in_database = vk_api_identifiers_exist.get('not_in_database')

    if not_in_database:
        await insert_vk_api_identifiers_which_are_not_in_database(not_in_database, session)

    mapped_res_and_source_ids = await get_users_res_ids_and_source_ids(vk_api_unique_identifiers, session)

    in_database = await check_if_profiles_of_users_exist_in_database(
        {tpl[-1] for tpl in mapped_res_and_source_ids}, session
    )

    if in_database:
        pass


async def get_unique_identifiers(data: List[Dict]) -> Set[int]:

    return {dct.get('source_id') for dct in data}


async def check_if_vk_api_identifiers_exist_in_database(vk_api_identifiers: Set[int], session: AsyncSession) -> Dict:

    stmt = select(Source.res_id).where(Source.source_id.in_(vk_api_identifiers))
    result = await session.execute(stmt)

    in_database = {data[-1] for data in result.fetchall()}
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

    in_database = {res[-1] for res in result.fetchall()}
    not_in_database = res_ids.difference(in_database)

    return {
        'in_database': in_database,
        'not_in_database': not_in_database
    }


async def insert_user_profiles(
        users_data: List[Dict],
        res_ids: Set[int],
        session: AsyncSession,
) -> Union[UserProfile, None]:

    select_stmt = select(Source.res_id, Source.source_id).where(Source.res_id.in_(res_ids))

    res_id_mapping = await session.execute(select_stmt)
    res_id_mapping = {row[0]: row[1] for row in res_id_mapping.fetchall()}

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
            user_profile.update(to_relational_fields)
            users_profiles_to_insert.append(user_profile)

    if users_profiles_to_insert:
        insert_stmt = insert(UserProfile).values(users_profiles_to_insert)
        result = await session.execute(insert_stmt)
        return result.scalar()


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


