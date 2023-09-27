import asyncio
import queue
from typing import Any
from vk_scraper_imas.utils import read_schema
from vk_scraper_imas.scarper import connector
from .tasks import TasksDistributor

RATE_LIMIT = 3


async def worker(tasks_queue: asyncio.Queue, token_queue: asyncio.Queue):

    task_distributor = TasksDistributor()

    while True:

        tasks = []
        for limit in range(RATE_LIMIT):
            if not tasks_queue.empty():
                task = await tasks_queue.get()
                tasks.append(task)

        token = await token_queue.get()

        async_tasks = [asyncio.create_task(
                task_distributor.call_api_method(
                    'get_users_info_by_vk_ids', task[0], token=token, fields=task[1]
                )
            ) for task in tasks]

        res = await asyncio.gather(*async_tasks)
        print(res)
        print(len(res))
        for task in tasks:
            await tasks_queue.put(task)
        await token_queue.put(token)
        await asyncio.sleep(1)




