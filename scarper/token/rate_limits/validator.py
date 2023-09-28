from typing import Final
from db_handler import APIStateDB


SUBSCRIBED_TO_GROUP_RATE_LIMIT: Final[int] = 3


class APIRateLimitsValidator:

    def __init__(self, obj_name: str, token: str):
        self._obj_name = obj_name
        self._token = token

    @property
    def obj_name(self) -> str:
        return self._obj_name

    @property
    def token(self) -> str:
        return self._token

    async def validate(self):

        validator = APIStateDB()

        await validator.create_state()


