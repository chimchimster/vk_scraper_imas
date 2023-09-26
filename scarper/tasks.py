import asyncio

from .queue import TokensQueue
from typing import List, Awaitable, Type, Union
from vk_scraper_imas.api.services import APIAsyncRequests


class TasksDistributor:

    __request_class = APIAsyncRequests
    __queue_class = TokensQueue
    __allowed_methods = [
        'get_users_info_by_vk_ids',
        'get_subscriptions_of_user_by_vk_id',
    ]

    @property
    def request_class(self) -> Type[APIAsyncRequests]:
        return self.__request_class

    @property
    def queue_class(self) -> Type[TokensQueue]:
        return self.__queue_class

    @property
    def allowed_methods(self) -> List:
        return self.__allowed_methods

    @staticmethod
    async def update_queue_if_empty(queue: TokensQueue, tasks: List[str]):
        """ Как только очередь закончилась, мы снова положим в нее те же самые ВК токены. """

        if queue.empty():
            await queue.put(tasks)

    async def get_token_from_queue(self, queue: TokensQueue, tasks: List[str]) -> str:
        """ Пытаемся получить токен из очереди. """

        try:
            if not queue.empty():
                return await queue.get()
        except asyncio.QueueEmpty:
            await self.update_queue_if_empty(queue, tasks)

    async def call_api_method(self, method_name: str, *args, **kwargs) -> Union[Awaitable, None]:
        """ Фабричный подход выбора нужного метода для очереди задач. """

        if method_name in self.allowed_methods:

            api_request_instance = self.request_class()

            api_method = getattr(api_request_instance, method_name)

            return await api_method(*args, **kwargs)





