import json
import asyncio

from typing import Any, Final, List

from vk_scraper_imas.utils import *
from vk_scraper_imas.scarpper import *
from vk_scraper_imas.database import *
from vk_scraper_imas.api.models import *
from vk_scraper_imas.api.utils.signals import *
from .token.rate_limits import *

RATE_LIMIT: Final[int] = 3
MAX_OFFSET_COUNT: Final[int] = 200


async def worker(
        tasks_queue: asyncio.Queue,
        tokens: List[str],
        task_distributor: TasksDistributor,
        logger=None,
):
    rate_limited = await read_schema(connector.schemas.rate_limited, 'rate_limited')

    semaphore = asyncio.Semaphore(50)

    while not tasks_queue.empty():

        zipped_tasks = []

        for token in tokens:
            tasks = await tasks_queue.get()

            if tasks:
                for task in tasks:
                    zipped_tasks.append((task, token))
                tasks_queue.task_done()
            else:
                break

        async_tasks = [
            asyncio.create_task(
                process_task(task_distributor, task, token, rate_limited, semaphore, logger)
            ) for task, token in zipped_tasks
        ]

        await logger.info(f'Выполняется {len(async_tasks)} задач.')
        await asyncio.gather(*async_tasks)
        await logger.info(f'Выполненно {len(async_tasks)} задач.')


async def process_task(task_distributor, task, token, rate_limited, semaphore, logger) -> None:

    task_model = task.model
    task_name = task.model.__name__

    response_model = ResponseModel()

    if task_name in rate_limited:
        validator = APIRateLimitsValidator(task_name, token)
        await validator.validate_state_before_request()

    async with (semaphore):

        if task_name == 'SubscribedToGroup':

            result_response = await task_distributor.call_api_method(
                task.coroutine_name, task.user_ids, fields=task.fields, token=token,
            )

            if not isinstance(result_response, dict):
                return

            count = result_response.get('response').get('count')

            if count and count > MAX_OFFSET_COUNT:

                offset = count // MAX_OFFSET_COUNT
                reminder = count % MAX_OFFSET_COUNT

                await handle_offset_for_subscribed_to_group(
                    task_distributor,
                    task,
                    token,
                    result_response,
                    offset,
                    reminder,
                )

        else:
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

            iterator_obj = model_handler.get(type(task_model))

            validated_models = []

            for response_data in iterator_obj:

                if not response_data:
                    return

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


async def handle_offset_for_subscribed_to_group(
        task_distributor,
        task,
        token: str,
        result_response: dict,
        offset: int,
        reminder: int
) -> None:

    async def extend_result_response(offset_count):

        result_with_offset = await task_distributor.call_api_method(
            task.coroutine_name, task.user_ids, fields=task.fields, token=token, offset=offset_count,
        )

        result_with_offset: dict

        if not result_with_offset:
            return

        response_with_offset = result_with_offset.get('response')

        if not response_with_offset or isinstance(result_with_offset, RateLimitSignal):
            return
        else:

            items = result_with_offset.get('items')

            if items:
                result_response['response']['items'].extend(items)

    for _ in range(offset):
        if result_response.get('response').get('count') == 1596:
            print(result_response.get('response').get('count'))
            print(len(result_response.get('response').get('items')))
        await extend_result_response(MAX_OFFSET_COUNT)
        await asyncio.sleep(1)
    else:
        if reminder:
            await extend_result_response(reminder)
            if result_response.get('response').get('count') == 1596:
                print(f'reminder: {reminder}', result_response.get('response').get('count'))


async def define_model_handler(
        mapping_response: ResponseModel,
        task_name: str,
) -> dict[type, dict | list | list[VKUser | SubscribedToUser | SubscribedToGroup | list] | None | Any]:
    # TODO: провести рефакторинг

    model_handlers = {}

    if task_name == 'VKUser':
        model_handlers[type(VKUser)] = mapping_response.response
    elif task_name == 'SubscribedToGroup':
        model_handlers[type(SubscribedToGroup)] = mapping_response.response.get('items')
    elif task_name == 'Wall':
        model_handlers[type(Wall)] = mapping_response.response.get('items')

    return model_handlers
