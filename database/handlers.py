from copy import deepcopy
from typing import List, Tuple, Dict

from sqlalchemy import select, func

from .models import *
from .common import *
from .auxilary import *
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
    res_ids_which_are_in_database = users_exist.get('in_database')

    if res_ids_which_are_not_in_database:

        await insert_user_profiles(users_data, res_ids_which_are_not_in_database, session)
        await insert_user_hashes(users_data, res_ids_which_are_not_in_database, session)
        await insert_initial_events(users_data, res_ids_which_are_not_in_database, session)
        await handle_last_seen(users_data, res_ids_which_are_in_database, session, flag='insert')

    if res_ids_which_are_in_database:

        await handle_last_seen(users_data, res_ids_which_are_in_database, session, flag='update')

        old_res_ids_and_hashes = await get_old_res_ids_and_hashes_of_users(
            res_ids_which_are_in_database,
            session,
        )

        new_res_ids_and_hashes = await get_new_res_ids_and_hashes_of_users(
            users_data,
            res_ids_which_are_in_database,
            session,
        )

        hashes_which_changed = old_res_ids_and_hashes.difference(new_res_ids_and_hashes)

        if hashes_which_changed:

            users_res_ids_which_hashes_changed = {res_id_hash[0] for res_id_hash in hashes_which_changed}

            users_data_which_hashes_changed_from_database = await get_users_data_which_hashes_changed(
                users_res_ids_which_hashes_changed,
                session,
            )

            if users_res_ids_which_hashes_changed:

                preprocessed_users_data = await preprocess_users_data_from_database(users_data)

                incoming_users_data_which_hashes_changed = await lead_user_data_to_single_representation(
                    preprocessed_users_data,
                )

                mapped_prev_and_cur_users_data = await map_pairs_of_incoming_and_existing_in_database_users_data(
                    incoming_users_data_which_hashes_changed,
                    users_data_which_hashes_changed_from_database,
                )

                new_events_generated = await generate_events_from_mapped_incoming_and_database_data(
                    mapped_prev_and_cur_users_data,
                )

                new_events_generated = [event for event in new_events_generated if event]

                if new_events_generated:

                    await insert_incoming_events(
                        new_events_generated,
                        session,
                    )

                    incoming_users_data_for_profiles = deepcopy(incoming_users_data_which_hashes_changed)
                    incoming_users_data_for_hashes = deepcopy(incoming_users_data_which_hashes_changed)

                    await update_users_profiles_which_hashes_changed(
                        users_res_ids_which_hashes_changed,
                        incoming_users_data_for_profiles,
                        session,
                    )

                    await update_user_hashes_which_has_been_changed(
                        users_res_ids_which_hashes_changed,
                        incoming_users_data_for_hashes,
                        session,
                    )


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

            await insert_subscription_into_source_subscription_profile(
                subscription_res_id, to_relational_fields_mapped, json_field, session
            )


@execute_transaction
async def get_source_ids(offset: int, limit: int, source_type: int = 1, **kwargs) -> List[Tuple]:
    """ Получение уникальных идентификаторов соцсети Вконтакте пользователей. """

    session = kwargs.get('session')

    stmt = (
        select(Source.source_id).where(Source.source_type == source_type).
        order_by(Source.res_id).
        offset(offset).
        limit(limit)
    )

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
