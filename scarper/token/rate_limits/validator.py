from typing import Union, Final

from vk_scraper_imas.api.models import SubscribedToGroup


SUBSCRIBED_TO_GROUP_RATE_LIMIT: Final[int] = 3


class APIRateLimitsValidator:

    def __init__(self, obj: SubscribedToGroup, token: str):
        self._obj = obj
        self._token = token



