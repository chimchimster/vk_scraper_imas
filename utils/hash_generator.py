import json
import hashlib

from typing import Dict
from datetime import datetime
from datetime import date
from .common import cleanup


async def generate_hash(res_id: int, response_dict: Dict):
    """ Генерация ключа по входным данным. """

    response_dict = await cleanup(response_dict)

    string = json.dumps(
        {
            key: value.strftime('%d-%m-%Y') if isinstance(value, date)
            else value for key, value in response_dict.items()
        }
    )

    return res_id, hashlib.sha256(string.encode()).hexdigest()


async def validate_hash(res_id: int, previous_hash: str, current_data: Dict) -> bool:

    return previous_hash == await generate_hash(res_id, current_data)
