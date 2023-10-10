import asyncio
import json
import time

from datetime import datetime, date
from typing import Dict, Union, List, Set, Tuple, Sequence, Any

from sqlalchemy import select, update, insert, join, Row, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert as insert_mysql

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
    res_id, new_hash = await generate_hash(user_res_id, data_to_hash)

    stmt = update(ScrapperHash).filter_by(res_id=res_id).values(social_info_hash=new_hash)
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


async def insert_upcoming_events(events: List[Dict], session):
    id_mapping = {}

    source_ids = [dct.get('id') for dct in events]

    events = [{event.pop('id'): event} for event in events]

    events = filter(lambda event: len(list(event.values())) > 0, events)

    stmt = select(Source.res_id, Source.source_id).where(Source.source_id.in_(source_ids))

    result = await session.execute(stmt)

    result_res_ids_and_source_ids = result.fetchall()

    for res_id, source_id in result_res_ids_and_source_ids:
        id_mapping[source_id] = res_id

    new_events = []
    for event in events:
        intermediate_dict = {}
        for key, value in event.items():
            res_id = id_mapping[key]
            intermediate_dict[res_id] = value
            new_events.append(intermediate_dict)

    now = int(time.time())

    map_events = []
    for event in new_events:
        for res_id, value in event.items():
            for event_type, event_value in value.items():
                new_events = [
                    {
                        'event_time': now,
                        'res_id': res_id,
                        'event_type': event_type,
                        'event_value': event_value,
                    }
                ]
                map_events.extend(new_events)

    if map_events:
        insert_stmt = insert(UserEvent).values(map_events)
        await session.execute(insert_stmt)


async def map_pairs_of_incoming_and_existing_in_database_users_data(
        incoming_data: Tuple[Dict],
        database_data: Tuple[Dict],
) -> List[Tuple[Dict, Dict]]:
    pairs = []

    tasks = [
        asyncio.create_task(flat_dict(data)) for data in incoming_data
    ]

    incoming_data = await asyncio.gather(*tasks)

    tasks = [
        asyncio.create_task(flat_dict(data)) for data in database_data
    ]

    database_data = await asyncio.gather(*tasks)

    database_dict = {dct['id']: dct for dct in database_data}

    for db_entry in incoming_data:
        if db_entry['id'] in database_dict:
            pairs.append((db_entry, database_dict[db_entry['id']]))

    return pairs


async def lead_user_data_to_single_representation(user_data: Tuple[Tuple[Dict, Dict]]) -> Tuple[Dict]:
    result_users_data = []

    for item in user_data:
        intermediate_dict = {}
        intermediate_dict.update(item[0])
        intermediate_dict['info_json'] = item[1]
        result_users_data.append(intermediate_dict)

    tasks = [
        asyncio.create_task(
            clear_user_data_up(user, flag='not_db')
        ) for user in result_users_data
    ]

    users_data = await asyncio.gather(*tasks)

    return users_data


async def get_unique_identifiers(data: List[Dict]) -> Set[int]:
    return {dct.get('id') for dct in data}


async def check_if_vk_api_identifiers_exist_in_database(vk_api_identifiers: Set[int], session: AsyncSession) -> Dict:

    stmt = select(Source.source_id).where(and_(Source.source_id.in_(vk_api_identifiers), Source.source_type == 1))
    result = await session.execute(stmt)

    in_database = {data[0] for data in result.fetchall()}
    not_in_database = vk_api_identifiers.difference(in_database)
    print(in_database)
    print(not_in_database)
    return {
        'in_database': in_database,
        'not_in_database': not_in_database,
    }


async def insert_vk_api_identifiers_which_are_not_in_database(
        vk_api_identifiers: Set,
        session: AsyncSession,
) -> Source:
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


async def insert_user_hashes(
        users_data: List[Dict],
        res_ids: Set[int],
        session: AsyncSession,
) -> None:
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


async def insert_initial_events(
        users_data: Union[List[Dict], Tuple[Dict]],
        res_ids: Set[int],
        session: AsyncSession,
) -> None:
    tasks = [
        asyncio.create_task(
            cleanup(user_data)
        ) for user_data in users_data
    ]

    users_data = await asyncio.gather(*tasks)

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


async def get_old_res_ids_and_hashes_of_users(
        res_ids: Set[int],
        session: AsyncSession,
) -> set[Row[tuple[Any, Any]]]:

    stmt = select(ScrapperHash.res_id, ScrapperHash.social_info_hash).where(ScrapperHash.res_id.in_(res_ids))

    result = await session.execute(stmt)

    res_ids_and_hashes = result.fetchall()

    return set(res_ids_and_hashes)


async def get_new_res_ids_and_hashes_of_users(
        users_data: Union[List[Dict], Tuple[Dict]],
        res_ids: Set[int],
        session: AsyncSession,
) -> Set[Tuple[int, str]]:
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

    return set(generated_hashes)


async def get_users_data_which_hashes_changed(
        res_ids: Set[int],
        session: AsyncSession,
) -> Tuple[Dict]:
    stmt = select(UserProfile, Source.source_id).select_from(
        join(Source, UserProfile, Source.res_id == UserProfile.res_id)
    ).where(UserProfile.res_id.in_(res_ids))

    result = await session.execute(stmt)

    result_data = result.fetchall()

    tasks = [
        asyncio.create_task(
            clear_user_data_up(res_d[0], source_id=res_d[1], flag='exist')
        ) for res_d in result_data
    ]

    users_data = await asyncio.gather(*tasks)

    return users_data


async def clear_user_data_up(
        user: Union[UserProfile, Dict],
        source_id: int = None,
        flag='exist',
) -> Dict:
    if flag == 'exist':
        user_dict = {key: json.loads(value) if key == 'info_json' else value for key, value in user.__dict__.items()}
        user_dict.update({'id': source_id})
    else:
        user_dict = {key: json.loads(value) if key == 'info_json' else value for key, value in user.items()}

    if user_dict.get('info_json').get('last_seen'):
        user_dict.get('info_json').pop('last_seen')

    return {
        key:
            value.strftime('%-d.%-m.%Y') if isinstance(value, date)
            else value
        for key, value in user_dict.items() if key not in (
            '_sa_instance_state',
            'res_id',
        )
    }


async def update_profiles_which_hashes_changed(
        users_data: List[Dict],
        res_ids: Set[int],
        session: AsyncSession,
) -> None:
    select_stmt = select(Source.res_id, Source.source_id).where(Source.res_id.in_(res_ids))

    res_id_mapping = await session.execute(select_stmt)
    res_id_mapping = {row[1]: row[0] for row in res_id_mapping.fetchall()}

    users_profiles_to_update = []
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
            users_profiles_to_update.append(user_profile)

    if users_profiles_to_update:
        stmt = update(UserProfile).values(users_profiles_to_update)
        await session.execute(stmt)


async def preprocess_users_data_from_database(users_data):
    tasks = [
        asyncio.create_task(
            prepare_data(user_data, flag='user')
        ) for user_data in users_data
    ]

    preprocessed_users_data = await asyncio.gather(*tasks)

    return preprocessed_users_data


async def generate_events_from_mapped_upcoming_and_database_data(
        mapped_data: List[Tuple[Dict, Dict]]
):
    tasks = [
        generate_event(prev_user_data, cur_user_data)
        for prev_user_data, cur_user_data in mapped_data
    ]

    new_events_generated = await asyncio.gather(*tasks)

    return new_events_generated


async def update_user_hashes_which_has_been_changed(
        res_ids: Set[int],
        users_data: Tuple[Dict],
        session: AsyncSession,
) -> None:
    select_stmt = select(Source.res_id, Source.source_id).where(Source.res_id.in_(res_ids))

    res_id_mapping = await session.execute(select_stmt)
    res_id_mapping = {row[1]: row[0] for row in res_id_mapping.fetchall()}

    user_data_ids_mapped = [
        {
            res_id_mapping.get(
                user_data.pop('id')
            ): user_data
        } for user_data in users_data
    ]

    tasks = []
    for user_data in user_data_ids_mapped:

        intermediate_dict = {}

        for res_id, response_dict in user_data.items():

            response_dict['birth_date'] = datetime.strptime(response_dict['birth_date'], '%d.%m.%Y')
            info_json = response_dict.pop('info_json')
            intermediate_dict.update(response_dict)
            intermediate_dict.update(info_json)

            tasks.append(generate_hash(res_id, intermediate_dict))

    res_ids_new_hashes = await asyncio.gather(*tasks)

    mapped_res_ids_hashes = [
        {
            'res_id': res_id,
            'social_info_hash': social_info_hash
        } for res_id, social_info_hash in res_ids_new_hashes
    ]

    insert_stmt = insert_mysql(ScrapperHash).values(mapped_res_ids_hashes)
    insert_stmt = insert_stmt.on_duplicate_key_update(
        res_id=insert_stmt.inserted.res_id,
        social_info_hash=insert_stmt.inserted.social_info_hash,
    )

    await session.execute(insert_stmt)


async def update_users_profiles_which_hashes_changed(
        res_ids: Set[int],
        users_data: Union[List[Dict], Tuple[Dict]],
        session: AsyncSession,
):
    select_stmt = select(Source.res_id, Source.source_id).where(Source.res_id.in_(res_ids))

    res_id_mapping = await session.execute(select_stmt)
    res_id_mapping = {row[1]: row[0] for row in res_id_mapping.fetchall()}

    user_data_ids_mapped = [
        {
            res_id_mapping.get(
                user_data.pop('id')
            ): user_data
        } for user_data in users_data
    ]
    print(user_data_ids_mapped)
    mapped_to_update = []
    for user_data in user_data_ids_mapped:
        intermediate_dict = {}
        for key, value in user_data.items():
            # TODO: ПРОДОЛЖИТЬ ОТСЮДА!
            if key:
                value['birth_date'] = datetime.strptime(value['birth_date'], '%d.%m.%Y')
                value['info_json'] = json.dumps(value['info_json'])
                intermediate_dict.update(value)
                intermediate_dict.update({'res_id': key})
        mapped_to_update.append(intermediate_dict)

    insert_stmt = insert_mysql(UserProfile).values(mapped_to_update)
    insert_stmt = insert_stmt.on_duplicate_key_update(
        user_name=insert_stmt.inserted.user_name,
        deactivated=insert_stmt.inserted.deactivated,
        is_closed=insert_stmt.inserted.is_closed,
        birth_date=insert_stmt.inserted.birth_date,
        profile_image=insert_stmt.inserted.profile_image,
        sex=insert_stmt.inserted.sex,
        info_json=insert_stmt.inserted.info_json,
    )

    await session.execute(insert_stmt)


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
    'update_profiles_which_hashes_changed',
    'clear_user_data_up',
    'get_users_data_which_hashes_changed',
    'get_new_res_ids_and_hashes_of_users',
    'get_old_res_ids_and_hashes_of_users',
    'insert_initial_events',
    'insert_user_hashes',
    'insert_user_profiles',
    'check_if_profiles_of_users_exist_in_database',
    'get_users_res_ids_and_source_ids',
    'get_unique_identifiers',
    'insert_vk_api_identifiers_which_are_not_in_database',
    'lead_user_data_to_single_representation',
    'map_pairs_of_incoming_and_existing_in_database_users_data',
    'insert_upcoming_events',
    'check_if_vk_api_identifiers_exist_in_database',
    'preprocess_users_data_from_database',
    'generate_events_from_mapped_upcoming_and_database_data',
    'update_user_hashes_which_has_been_changed',
    'update_users_profiles_which_hashes_changed',
]
