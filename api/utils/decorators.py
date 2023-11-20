import json
import aiohttp

from functools import wraps
from typing import Awaitable, Optional, Callable

from vk_scraper_imas.api.exceptions import VKAPIException
from vk_scraper_imas.logs import stream_logger
from .signals import *


def do_post_request_to_vk_api(func: Optional[Callable[..., Awaitable[None]]]):
    @wraps(func)
    async def wrapper(*args, **kwargs):

        request_string = await func(*args, **kwargs)

        timeout = aiohttp.ClientTimeout(connect=10)

        try:
            async with aiohttp.ClientSession(
                json_serialize=json.dumps,
                timeout=timeout,
            ) as session:
                async with session.post(request_string) as response:
                    if response.status == 200:

                        response_str = await response.text()

                        response_json = json.loads(response_str)

                        signal = await check_errors(response_json)

                        if not signal:
                            return response_json
                        return signal
                    else:
                        await stream_logger.info(f"HTTP POST завершился со статус кодом {response.status}")

        except aiohttp.ServerTimeoutError as ste:
            await stream_logger.info(str(ste))
        except aiohttp.ServerConnectionError as sce:
            await stream_logger.info(str(sce))
        except VKAPIException as vk_api_exc:
            await stream_logger.info(str(vk_api_exc))

    return wrapper


async def check_errors(response_json):
    if response_json.get('error'):
        error_code = response_json['error']['error_code']
        if error_code == 29:
            return RateLimitSignal()
        if error_code == 30:
            return PrivateProfileSignal()
        if error_code == 18:
            return PageLockedOrDeletedSignal()
        if error_code == 5:
            return AuthorizationFailedSignal()

    return None

