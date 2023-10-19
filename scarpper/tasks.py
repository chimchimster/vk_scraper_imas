from typing import List, Awaitable, Type, Union, Final, Dict
from api.services import APIAsyncRequests
from api.models import *

RATE_LIMIT: Final[int] = 3


class TaskObject:

    __model_classes__ = {
        'get_users_info_by_vk_ids':  VKUser,
        'get_subscriptions_of_user_by_vk_id': SubscribedToGroup,
        'get_posts_by_vk_id': Wall,
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
    def model(self) -> Type[VKUser] | Type[SubscribedToGroup] | None:
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

    __task_instance = TaskObject
    __request_class_instance = APIAsyncRequests

    __allowed_methods = [
        'get_users_info_by_vk_ids',
        'get_subscriptions_of_user_by_vk_id',
        'get_posts_by_vk_id',
    ]

    __grouping_limits = {
        'VKUser': 500,
        'SubscribedToGroup': 1,
        'Wall': 1,
    }

    @property
    def request_class_instance(self) -> Type[APIAsyncRequests]:
        return self.__request_class_instance

    @property
    def allowed_methods(self) -> List:
        return self.__allowed_methods

    @property
    def grouping_limits(self) -> Dict:
        return self.__grouping_limits

    async def call_api_method(self, method_name: str, *args, **kwargs) -> Union[Awaitable, None]:
        """ Фабричный подход выбора нужного метода для очереди задач. """

        if method_name in self.allowed_methods:

            api_request_instance = self.request_class_instance()

            api_method = getattr(api_request_instance, method_name)

            return await api_method(*args, **kwargs)

    async def group(
            self,
            vk_ids: List[int],
            task_name: str,
            fields: List[str] = None,
            coroutine_name: str = None,
    ) -> List[List[TaskObject]]:

        limit = self.grouping_limits.get(task_name)

        tasks = [TaskObject(vk_ids[start:start + limit], fields, coroutine_name) for start in range(0, len(vk_ids), limit)]

        chunked_tasks = [tasks[start:start+RATE_LIMIT] for start in range(len(tasks))]

        return chunked_tasks





