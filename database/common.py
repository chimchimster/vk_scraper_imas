import json
from datetime import datetime
from typing import Final, List, Dict, Union, Tuple

KEYS_NAMES_FOR_CLEANING_USER_UP: Final[List] = [
    'id',
    'first_name',
    'last_name',
    'deactivated',
    'is_closed',
    'sex',
    'bdate',
    'photo_max_orig',
]

MAP_VK_KEYS_AND_USER_PROFILE_DATABASE_FIELDS: Final[Dict] = {
    'bdate': 'birth_date',
    'photo_max_orig': 'profile_image',
}

KEYS_NAMES_FOR_CLEANING_SUBSCRIPTION_UP: Final[List] = [
    'id',
    'name',
    'is_closed',
    'deactivated',
    'members_count',
    'photo_200',
]

MAP_VK_KEYS_AND_SUBSCRIPTION_PROFILE_DATABASE_FIELDS: Final[Dict] = {
    'name': 'subscription_name',
    'photo_200': 'profile_image',
}


async def prepare_data(
    data: Dict,
    flag: str = None,
) -> Union[Tuple[Dict, str], Tuple[Dict, str, int]]:

    if flag == 'user':
        to_relational_fields = await cleanup_data(
            data,
            delta=False,
            mapping_keys=KEYS_NAMES_FOR_CLEANING_USER_UP,
        )
        to_relational_fields_mapped = await map_api_keys_with_database_fields(
            to_relational_fields,
            flag=flag,
            mapping_dict=MAP_VK_KEYS_AND_USER_PROFILE_DATABASE_FIELDS,
        )
        to_json_field = await cleanup_data(data, delta=True, mapping_keys=KEYS_NAMES_FOR_CLEANING_USER_UP)
        to_json_field.pop('last_seen')
        json_field = json.dumps(to_json_field)
        return to_relational_fields_mapped, json_field
    else:
        to_relational_fields = await cleanup_data(
            data,
            delta=False,
            mapping_keys=KEYS_NAMES_FOR_CLEANING_SUBSCRIPTION_UP,
        )
        to_relational_fields_mapped = await map_api_keys_with_database_fields(
            to_relational_fields,
            flag=flag,
            mapping_dict=MAP_VK_KEYS_AND_SUBSCRIPTION_PROFILE_DATABASE_FIELDS,
        )
        to_json_field = await cleanup_data(data, delta=True, mapping_keys=KEYS_NAMES_FOR_CLEANING_SUBSCRIPTION_UP)
        source_id = to_relational_fields_mapped.pop('id')
        json_field = json.dumps(to_json_field)
        return to_relational_fields_mapped, json_field, source_id


async def cleanup_data(
        user_data: Dict,
        delta: bool = False,
        mapping_keys: List[str] = None) -> Dict:
    """ Отчистка данных пользователя от неиспользуемых ключей. """

    return {key: value for key, value in user_data.items() if (key not in mapping_keys) == delta}


async def map_api_keys_with_database_fields(vk_dict: Dict, flag: str = None, mapping_dict: Dict = None) -> Dict:
    """ Сопоставление ключей пользователя и пользовательской подписки с API вконтакте с полями базы данных. """

    if flag == 'user':
        to_relational_fields_dict = {'user_name': ''}
    else:
        to_relational_fields_dict = {}

    for key, value in vk_dict.items():

        if flag == 'user' and key in ('first_name', 'last_name'):
            to_relational_fields_dict['user_name'] += value + ' '
            continue

        if key in mapping_dict.keys():
            to_relational_fields_dict[mapping_dict[key]] = value
            continue

        to_relational_fields_dict[key] = value

    if flag == 'user':
        if to_relational_fields_dict['user_name'].lower().strip() == 'deleted':
            to_relational_fields_dict['user_name'] = str(to_relational_fields_dict['id'])
        else:
            to_relational_fields_dict['user_name'] = to_relational_fields_dict['user_name'][:-1]

        birth_date = to_relational_fields_dict['birth_date']

        to_relational_fields_dict['birth_date'] = await handle_birthdate(birth_date)

    return to_relational_fields_dict


async def handle_birthdate(birth_date: str) -> Union[datetime, None]:
    """ Взято из моего старого скрипта за неимением времени.
    TODO: необходим более универсальный алгоритм, рефакторинг. """

    if not birth_date:
        return

    date_of_birth = birth_date.split('.')

    if len(date_of_birth) < 3:
        return

    async def number_checker(nbr: str):
        if len(nbr) < 2:
            nbr = '0' + nbr
        return nbr

    universalized = []
    for date in date_of_birth:
        number = await number_checker(date)
        universalized.append(number)

    return datetime.strptime('.'.join(universalized), "%d.%m.%Y")


async def flat_dict(data_dict: Dict) -> Dict:

    flt_dict = {}
    for key, value in data_dict.items():
        if isinstance(value, dict):
            nested_items = await flat_dict(value)
            flt_dict.update(nested_items)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    nested_items = await flat_dict(item)
                    flt_dict.update(nested_items)
        else:
            flt_dict[key] = value

    return flt_dict


__all__ = [
    'prepare_data',
    'flat_dict',
]
