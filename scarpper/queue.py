import json
import sys
import asyncio
import time

from typing import Any, Final, Dict, Type, List

from utils import *
from scarpper import *
from database import *
from api.models import *
from api.utils.signals import *
from .token.rate_limits import *


RATE_LIMIT: Final[int] = 3


async def worker(tasks_queue: asyncio.Queue, token_queue: asyncio.Queue, task_distributor: TasksDistributor):

    rate_limited = await read_schema(connector.schemas.rate_limited, 'rate_limited')

    semaphore = asyncio.Semaphore(20)

    while not tasks_queue.empty():

        async_tasks = []

        buffer_token_queue = asyncio.Queue()

        while not token_queue.empty():

            tasks = await tasks_queue.get()

            token = await token_queue.get()

            await buffer_token_queue.put(token)

            for task in tasks:
                if task:
                    async_tasks.append(process_task(task_distributor, task, token, rate_limited, semaphore))

            tasks_queue.task_done()
            token_queue.task_done()

        while not buffer_token_queue.empty():
            token = await buffer_token_queue.get()
            await token_queue.put(token)

        start_time = time.perf_counter()
        print('Выполняется задач: ', len(async_tasks), ' Время начала выполнения: ', start_time)
        await asyncio.gather(*async_tasks)
        end_time = time.perf_counter()
        print('Выполнилось задач: ', len(async_tasks), ' Время завершения выполнения', end_time - start_time)

async def process_task(task_distributor, task, token, rate_limited, semaphore) -> None:

    if not task:
        return

    task_model = task.model
    task_name = task.model.__name__

    response_model = ResponseModel()

    if task_name in rate_limited:
        validator = APIRateLimitsValidator(task_name, token)
        await validator.validate_state_before_request()

    async with (semaphore):
        try:
            result_response = await task_distributor.call_api_method(
                task.coroutine_name, task.user_ids, fields=task.fields, token=token,
            )

            if any(
                    map(
                        lambda signal: isinstance(result_response, signal),
                        [PrivateProfileSignal, PageLockedOrDeletedSignal, AuthorizationFailedSignal]
                    )
            ):
                return

            has_signal = isinstance(result_response, RateLimitSignal)
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

                    validated_data = task_model.model_validate(response_data)
                    validated_models.append(validated_data)

                if task_name == 'VKUser':

                    await users_handler(
                        [
                            json.loads(model.json()) for model in validated_models
                        ]
                    )

                elif task_name == 'SubscribedToGroup':

                    tasks = [
                        asyncio.create_task(
                            subscription_handler(json.loads(model.json()), task.user_ids)
                        ) for model in validated_models
                    ]

                    await asyncio.gather(*tasks)

        except Exception as e:
            sys.stderr.write(f"An error occurred: {str(e)}")


async def define_model_handler(
        mapping_response: ResponseModel,
        task_name: str,
) -> Dict[Type[VKUser | SubscribedToGroup], List | None | Any]:
    # TODO: провести рефакторинг

    model_handlers = {}

    if task_name == 'VKUser':
        model_handlers[VKUser] = mapping_response.response
    elif task_name == 'SubscribedToGroup':
        model_handlers[SubscribedToGroup] = mapping_response.response.get('items')
    elif task_name == 'Wall':
        model_handlers[Wall] = mapping_response.response.get('items')

    return model_handlers
