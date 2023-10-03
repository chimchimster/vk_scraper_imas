import asyncio
import hashlib
import json


class HashGenerator:

    __dynamic_data = [
        'followers_count',
        'last_seen',
    ]

    def __init__(self, response_dict: dict):
        self._response_dict = response_dict

    @property
    def response_dict(self) -> dict:
        return self._response_dict

    @property
    def dynamic_data(self) -> list:
        return self.__dynamic_data

    async def cleanup(self):
        """ Необходимо отчистить входной словарь от динамических данных. """

        for key in self.dynamic_data:
            if key in self.response_dict:
                self.response_dict.pop(key)

    async def generate_hash(self):
        """ Генерация ключа по входным данным. """

        await self.cleanup()

        string = json.dumps(self.response_dict)

        return hashlib.sha256(string.encode()).hexdigest()