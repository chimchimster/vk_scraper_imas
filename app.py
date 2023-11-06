import math
import asyncio

from typing import Final
from asyncio import Queue

from database import *
from utils import read_schema
from logs import stream_logger
from scarpper import TasksDistributor, worker, connector

SOURCE_IDS_OFFSET: Final[int] = 1500
SUBSCRIPTION_LIMIT: Final[int] = 10000
SUBSCRIPTION_OFFSET: Final[int] = 200


async def main():

    task_distributor = TasksDistributor()

    tokens = await read_schema(connector.schemas.path_to_tokens, 'tokens')

    tasks_queue = Queue()
    start_offset = 0

    while True:

        user_fields = await read_schema(connector.schemas.user_fields, 'user_fields')
        group_fields = await read_schema(connector.schemas.group_fields, 'group_fields')

        source_ids_count = await get_source_ids_count()

        iteration_count = math.ceil(source_ids_count / SOURCE_IDS_OFFSET)

        for iteration in range(iteration_count):

            source_ids = await get_source_ids(SOURCE_IDS_OFFSET * iteration, SOURCE_IDS_OFFSET)

            source_ids = list(map(int, [fetched_id[-1] for fetched_id in source_ids]))

            task_objs_vk_user = await task_distributor.group(
                source_ids,
                'VKUser',
                fields=user_fields,
                coroutine_name='get_users_info_by_vk_ids',
            )

            task_objs_subscribed_to_group = await task_distributor.group(
                source_ids,
                'SubscribedToGroup',
                fields=group_fields,
                coroutine_name='get_subscriptions_of_user_by_vk_id'
            )

            task_objs = []
            task_objs.extend(task_objs_vk_user)
            task_objs.extend(task_objs_subscribed_to_group)

            for task in task_objs:
                await tasks_queue.put(task)

        await worker(tasks_queue, tokens, task_distributor, logger=stream_logger, offset=start_offset)

        if start_offset <= SUBSCRIPTION_LIMIT:
            start_offset += SUBSCRIPTION_OFFSET
        else:
            start_offset = 0

        print(start_offset)

if __name__ == '__main__':
    asyncio.run(main())

