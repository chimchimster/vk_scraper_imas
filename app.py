import asyncio

from config_reader import config
from utils import read_schema
from scarper import TasksDistributor, TokensQueue, connector


async def main():

    user_ids = ['id226245594', 'dmitriy_panfilov', 'angieozerova', 'dosia1488', 'favnart', 'aslushnikov']

    tokens = config.vk_token.get_secret_value().split(',')

    queue = TokensQueue()
    task_distributor = TasksDistributor()

    # TODO: NOW FORM COROUTINES FOR ALL OPERATIONS ALLOWED BY TOKENS, SEND REQS AND INSERT DATA IN DATABASE
    await task_distributor.get_token_from_queue(queue, tokens)

    res = await read_schema(connector.schemas.user_fields)
    print(res)

if __name__ == '__main__':
    asyncio.run(main())

