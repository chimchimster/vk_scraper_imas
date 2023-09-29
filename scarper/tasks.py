from typing import List, Awaitable, Type, Union
from vk_scraper_imas.api.services import APIAsyncRequests
from vk_scraper_imas.api.models import VKUser, SubscribedToGroup, SubscribedToUser


class TaskObject:

    __model_classes__ = {
        'get_users_info_by_vk_ids':  VKUser,
        'get_subscriptions_of_user_by_vk_id': SubscribedToGroup,
    }

    def __init__(self, user_ids: Union[List, str], fields: List[str], coroutine_name: str):
        self.__user_ids = user_ids
        self.__fields = fields
        self.__coroutine_name = coroutine_name
        self.__model = self.__define_model()

    @property
    def coroutine_name(self) -> Union[str, None]:
        return self.__coroutine_name

    @property
    def model(self) -> Union[VKUser, SubscribedToGroup, SubscribedToUser]:
        return self.__model

    @property
    def user_ids(self) -> Union[List, str]:
        return self.__user_ids

    @property
    def fields(self) -> List[str]:
        return self.__fields

    def __define_model(self):
        return self.__model_classes__.get(self.coroutine_name)

    def __iter__(self):
        yield self


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






