import asyncio
import queue
import sys
from typing import Any

from pydantic import ValidationError

from vk_scraper_imas.utils import read_schema
from vk_scraper_imas.scarper import connector
from .tasks import TasksDistributor
from vk_scraper_imas.api.models import ResponseModel, VKUser, SubscribedToGroup
from token.rate_limits import APIRateLimitsValidator

response_model = ResponseModel()

RATE_LIMIT = 3


async def worker(tasks_queue: asyncio.Queue, token_queue: asyncio.Queue):

    task_distributor = TasksDistributor()

    rate_limited = await read_schema(connector.schemas.rate_limited, 'rate_limited')

    while True:

        tasks = await tasks_queue.get()
        token = await token_queue.get()

        if tasks.model.__name__ in rate_limited:
            # TODO: VALIDATION OF TOKENS
            validator = APIRateLimitsValidator(tasks.model.__name__, token)
            await validator.validate()

        async_tasks = [asyncio.create_task(
                task_distributor.call_api_method(
                    task.coroutine_name, task.user_ids, fields=task.fields, token=token,
                )
            ) for task in tasks]

        result_responses = await asyncio.gather(*async_tasks)

        mapping_responses = map(lambda responses: response_model.model_validate(responses), result_responses)

        user_models_mapping = [obj for obj in zip([task.model for task in tasks], mapping_responses)]

        model_handlers = {
            VKUser: lambda rsp_data: rsp_data.response,
            SubscribedToGroup: lambda rsp_data: rsp_data.response.get('items')
        }

        validated_models = []
        for user_model, response_data in user_models_mapping:

            if not response_data:
                break

            handler = model_handlers.get(user_model)

            if not handler:
                continue

            iterator_obj = handler(response_data)

            if not iterator_obj:
                continue

            for res_mdl in iterator_obj:
                try:
                    validated_data = user_model.model_validate(res_mdl)
                    validated_models.append(validated_data)
                except ValidationError as v:
                    sys.stderr.write(str(v))

            print(validated_models)

        for task in tasks:
            await tasks_queue.put(task)

        await token_queue.put(token)
        await asyncio.sleep(1)




