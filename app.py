import asyncio

from utils import read_schema
from scarper import TasksDistributor, TaskObject, worker, connector
from api.models import ResponseModel, VKUser, SubscribedToGroup, SubscribedToUser


RATE_LIMIT = 3


async def main():

    user_ids1 = ['id226245594', 'dmitriy_panfilov', 'angieozerova', 'dosia1488', 'favnart', 'aslushnikov']
    user_ids2 = ['id121389', 'id628380', 'id121888']
    user_ids3 = ['id140480', 'batwoman_nax', 'maxim_solomin']
    user_ids4 = ['id13055', 'roganov', 'anastasina']
    user_ids5 = ['smolyanka', 'vpavlov', 'dummyfox']
    user_ids6 = 281818828

    tokens = await read_schema(connector.schemas.path_to_tokens, 'tokens')

    user_fields = await read_schema(connector.schemas.user_fields, 'user_fields')
    group_fields = await read_schema(connector.schemas.group_fields, 'group_fields')

    tasks_queue = asyncio.Queue()
    tokens_queue = asyncio.Queue()

    await tokens_queue.put(*tokens)

    task_objects = []

    task_obj1 = TaskObject(user_ids1, user_fields, 'get_users_info_by_vk_ids')
    task_obj2 = TaskObject(user_ids2, user_fields, 'get_users_info_by_vk_ids')
    task_objects.append(task_obj1)
    task_objects.append(task_obj2)

    task_obj3 = TaskObject(user_ids6, group_fields, 'get_subscriptions_of_user_by_vk_id')
    task_objects.append(task_obj3)

    for task_obj in task_objects:
        await tasks_queue.put(task_obj)

    await worker(tasks_queue, tokens_queue)

    # TODO: NOW FORM COROUTINES FOR ALL OPERATIONS ALLOWED BY TOKENS, SEND REQS AND INSERT DATA IN DATABASE


if __name__ == '__main__':
    asyncio.run(main())

