import asyncio

from typing import List, Awaitable, Type, Union
from vk_scraper_imas.api.services import APIAsyncRequests


class TasksDistributor:

    __request_class = APIAsyncRequests
    __allowed_methods = [
        'get_users_info_by_vk_ids',
        'get_subscriptions_of_user_by_vk_id',
    ]

    @property
    def request_class(self) -> Type[APIAsyncRequests]:
        return self.__request_class

    @property
    def allowed_methods(self) -> List:
        return self.__allowed_methods

    async def call_api_method(self, method_name: str, *args, **kwargs) -> Union[Awaitable, None]:
        """ Фабричный подход выбора нужного метода для очереди задач. """

        if method_name in self.allowed_methods:

            api_request_instance = self.request_class()

            api_method = getattr(api_request_instance, method_name)

            return await api_method(*args, **kwargs)






