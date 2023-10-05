from datetime import datetime
from typing import Final, List, Dict, Union

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


async def cleanup_user_profile_data(user_data: Dict, delta: bool) -> Dict:
    """ Отчистка данных пользователя от неиспользуемых ключей. """

    return {key: value for key, value in user_data.items() if (key not in KEYS_NAMES_FOR_CLEANING_USER_UP) == delta}


async def map_vk_user_keys_with_database_fields(vk_dict: Dict) -> Dict:
    """ Сопоставление ключей пользователя с API вконтакте с полями базы данных. """

    to_relational_fields_dict = {'user_name': ''}

    for key, value in vk_dict.items():
        if key in ('first_name', 'last_name'):

            to_relational_fields_dict['user_name'] += value + ' '
            continue

        if key in MAP_VK_KEYS_AND_USER_PROFILE_DATABASE_FIELDS.keys():
            to_relational_fields_dict[MAP_VK_KEYS_AND_USER_PROFILE_DATABASE_FIELDS[key]] = value
            continue

        to_relational_fields_dict[key] = value

    if to_relational_fields_dict['user_name'].lower().strip() == 'deleted':
        to_relational_fields_dict['user_name'] = str(to_relational_fields_dict['id'])
    else:
        to_relational_fields_dict['user_name'] = to_relational_fields_dict['user_name'][:-1]

    birth_date = to_relational_fields_dict['birth_date']

    to_relational_fields_dict['birth_date'] = await handle_birthdate(birth_date)

    return to_relational_fields_dict


async def cleanup_subscription_profile_data(data: Dict, delta: bool) -> Dict:
    """ Отчистка данных подписки от неиспользуемых ключей. """

    return {key: value for key, value in data.items() if (key not in KEYS_NAMES_FOR_CLEANING_SUBSCRIPTION_UP) == delta}


async def map_vk_subscription_keys_with_database_fields(vk_dict: Dict) -> Dict:
    """ Сопоставление ключей пользовательской подписки с API вконтакте с полями базы данных. """

    to_relational_fields_dict = {}

    for key, value in vk_dict.items():
        if key in MAP_VK_KEYS_AND_SUBSCRIPTION_PROFILE_DATABASE_FIELDS.keys():
            to_relational_fields_dict[MAP_VK_KEYS_AND_SUBSCRIPTION_PROFILE_DATABASE_FIELDS[key]] = value
            continue

        to_relational_fields_dict[key] = value

    return to_relational_fields_dict


async def handle_birthdate(birth_date: str) -> Union[datetime, None]:
    """ Взято из моего старого скрипта за неимением времени. TODO: необходим более универсальный алгоритм, рефакторинг. """

    if not birth_date:
        return

    date_of_birth = birth_date.split('.')

    if len(date_of_birth) < 3:
        return

    def number_checker(number: str):
        if len(number) < 2:
            number = '0' + number
        return number

    universalized = []
    for date in date_of_birth:
        universalized.append(number_checker(date))

    return datetime.strptime('.'.join(universalized), "%d.%m.%Y")


__all__ = [
    'map_vk_user_keys_with_database_fields',
    'cleanup_user_profile_data',
    'cleanup_subscription_profile_data',
    'map_vk_subscription_keys_with_database_fields',
]
