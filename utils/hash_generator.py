import asyncio
import json
import hashlib

from typing import Dict
from datetime import datetime


DYNAMIC_DATA = [
    'followers_count',
    'last_seen',
]


async def generate_hash(res_id: int, response_dict: Dict):
    """ Генерация ключа по входным данным. """

    async def cleanup():
        """ Необходимо отчистить входной словарь от динамических данных. """

        for key in DYNAMIC_DATA:
            if key in response_dict:
                response_dict.pop(key)

    await cleanup()

    string = json.dumps(
        {
            key: value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime)
            else value for key, value in response_dict.items()
        }
    )
    print(hashlib.sha256(string.encode()).hexdigest())
    return res_id, hashlib.sha256(string.encode()).hexdigest()


async def validate_hash(previous_hash: str, current_data: Dict) -> bool:

    return previous_hash == await generate_hash(current_data)
