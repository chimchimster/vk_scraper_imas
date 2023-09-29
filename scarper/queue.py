import asyncio
import queue
import sys
from typing import Any, Final

from pydantic import ValidationError

from vk_scraper_imas.utils import read_schema
from vk_scraper_imas.scarper import connector
from .tasks import TasksDistributor
from vk_scraper_imas.api.models import ResponseModel, VKUser, SubscribedToGroup
from vk_scraper_imas.scarper.token.rate_limits import APIRateLimitsValidator
from vk_scraper_imas.api.utils.signals import ResponseSignal


RATE_LIMIT: Final[int] = 3


async def worker(tasks_queue: asyncio.Queue, token_queue: asyncio.Queue):
    task_distributor = TasksDistributor()

    rate_limited = await read_schema(connector.schemas.rate_limited, 'rate_limited')

    semaphore = asyncio.Semaphore(10)

    while True:

        task = await tasks_queue.get()
        token = await token_queue.get()
        await token_queue.put(token)

        task_name = task.model.__name__

        validator = APIRateLimitsValidator(task_name, token)
        await validator.validate_state_before_request()

        await process_task(task_distributor, task, token, rate_limited, semaphore)

        await tasks_queue.put(task)

        await asyncio.sleep(1)


async def process_task(task_distributor, task, token, rate_limited, semaphore):

    task_name = task.model.__name__
    task_model = task.model

    response_model = ResponseModel()

    async with semaphore:
        try:
            result_response = await task_distributor.call_api_method(
                task.coroutine_name, task.user_ids, fields=task.fields, token=token,
            )

            has_signal = isinstance(result_response, ResponseSignal)

            validator = APIRateLimitsValidator(task_name, token)
            validation_has_been_passed = await validator.validate_state_after_request(signal=has_signal)

            if validation_has_been_passed and result_response is not None:

                mapping_response = response_model.model_validate(result_response)
                print(mapping_response.response)
                model_handlers = {
                    VKUser: mapping_response.response,
                    # TODO: Проблема в том, что модель промежуточную ITEMS нужно провалидировать!
                    SubscribedToGroup: mapping_response.response
                }

                iterator_obj = model_handlers.get(task_model)

                validated_models = []
                for response_data in iterator_obj:

                    if not response_data:
                        break

                    try:
                        validated_data = task_model.model_validate(response_data)
                        validated_models.append(validated_data)
                    except ValidationError as v:
                        sys.stderr.write(str(v))

                print(validated_models)
        except Exception as e:
            sys.stderr.write(f"An error occurred: {str(e)}")

