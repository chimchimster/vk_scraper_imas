import json

from typing import List, Tuple, Dict

from sqlalchemy import select, func

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

                if hash_has_been_changed:
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


