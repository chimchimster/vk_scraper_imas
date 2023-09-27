import asyncio

from utils import read_schema
from scarper import TasksDistributor, worker, connector
from api.models import ResponseModel, VKUser, SubscribedToGroup, SubscribedToUser


RATE_LIMIT = 3


async def main():

    user_ids1 = ['id226245594', 'dmitriy_panfilov', 'angieozerova', 'dosia1488', 'favnart', 'aslushnikov']
    user_ids2 = ['id121389', 'id628380', 'id121888']
    user_ids3 = ['id140480', 'batwoman_nax', 'maxim_solomin']
    user_ids4 = ['id13055', 'roganov', 'anastasina']
    user_ids5 = ['smolyanka', 'vpavlov', 'dummyfox']

    tokens = await read_schema(connector.schemas.path_to_tokens, 'tokens')

    fields = await read_schema(connector.schemas.user_fields, 'user_fields')

    tasks_queue = asyncio.Queue()
    tokens_queue = asyncio.Queue()

    await tokens_queue.put(*tokens)
    await tasks_queue.put((user_ids1, fields))
    await tasks_queue.put((user_ids2, fields))
    await tasks_queue.put((user_ids3, fields))
    await tasks_queue.put((user_ids4, fields))
    await tasks_queue.put((user_ids5, fields))

    await worker(tasks_queue, tokens_queue)


    # TODO: NOW FORM COROUTINES FOR ALL OPERATIONS ALLOWED BY TOKENS, SEND REQS AND INSERT DATA IN DATABASE

if __name__ == '__main__':
    asyncio.run(main())

