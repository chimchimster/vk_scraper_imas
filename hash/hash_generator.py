import json
import hashlib

from typing import Dict


DYNAMIC_DATA = [
    'followers_count',
    'last_seen',
]


async def generate_hash(response_dict: Dict):
    """ Генерация ключа по входным данным. """

    async def cleanup():
        """ Необходимо отчистить входной словарь от динамических данных. """

        for key in DYNAMIC_DATA:
            if key in response_dict:
                response_dict.pop(key)

    await cleanup()

    string = json.dumps(response_dict)

    return response_dict.get('id'), hashlib.sha256(string.encode()).hexdigest()
