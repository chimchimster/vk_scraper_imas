import asyncio
import queue
import sys
from typing import Any, Final, Dict, Type, List

from pydantic import ValidationError

from vk_scraper_imas.utils import read_schema
from vk_scraper_imas.scarper import connector
from .tasks import TasksDistributor
from vk_scraper_imas.api.models import *
from vk_scraper_imas.scarper.token.rate_limits import APIRateLimitsValidator
from vk_scraper_imas.api.utils.signals import ResponseSignal


RATE_LIMIT: Final[int] = 3


async def worker(tasks_queue: asyncio.Queue, token_queue: asyncio.Queue):
    task_distributor = TasksDistributor()

    rate_limited = await read_schema(connector.schemas.rate_limited, 'rate_limited')

    semaphore = asyncio.Semaphore(10)

    while True:

        tasks = await tasks_queue.get()
        token = await token_queue.get()
        await token_queue.put(token)

        async_tasks = [process_task(task_distributor, task, token, rate_limited, semaphore) for task in tasks]

        await asyncio.gather(*async_tasks)

        await tasks_queue.put(tasks)

        await asyncio.sleep(1)


async def process_task(task_distributor, task, token, rate_limited, semaphore):

    task_model = task.model
    task_name = task.model.__name__

    response_model = ResponseModel()

    if task_name in rate_limited:
        validator = APIRateLimitsValidator(task_name, token)
        await validator.validate_state_before_request()

    async with semaphore:
        try:
            result_response = await task_distributor.call_api_method(
                task.coroutine_name, task.user_ids, fields=task.fields, token=token,
            )

            has_signal = isinstance(result_response, ResponseSignal)

            validation_has_been_passed = True

            if task_name in rate_limited:

                validator = APIRateLimitsValidator(task_name, token)
                validation_has_been_passed = await validator.validate_state_after_request(signal=has_signal)

            if validation_has_been_passed and result_response is not None:
                mapping_response = response_model.model_validate(result_response)

                model_handler = await define_model_handler(mapping_response, task_name)

                iterator_obj = model_handler.get(task_model)

                validated_models = []
                for response_data in iterator_obj:

                    if not response_data:
                        break

                    try:
                        validated_data = task_model.model_validate(response_data)
                        validated_models.append(validated_data)
                    except ValidationError as v:
                        sys.stderr.write(str(v))

                for model in validated_models:
                    print(model, end='\n')
        except Exception as e:
            sys.stderr.write(f"An error occurred: {str(e)}")


async def define_model_handler(
        mapping_response: ResponseModel,
        task_name: str,
) -> Dict[Type[VKUser | SubscribedToGroup], List | None | Any]:

    model_handlers = {}

    if task_name == 'VKUser':
        model_handlers[VKUser] = mapping_response.response
    elif task_name == 'SubscribedToGroup':
        model_handlers[SubscribedToGroup] = mapping_response.response.get('items')
    elif task_name == 'UserWall':
        model_handlers[UserWall] = mapping_response.response.get('items')

    return model_handlers
