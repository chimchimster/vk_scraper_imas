from typing import Dict


DYNAMIC_DATA = [
    'followers_count',
    'last_seen',
]


async def cleanup(response_dict: Dict) -> Dict:
    """ Отчистка входного словаря от динамических данных. """

    for key in DYNAMIC_DATA:
        if key in response_dict:
            response_dict.pop(key)

    return response_dict
