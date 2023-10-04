import json
import sys
from functools import wraps
from typing import Awaitable, Optional, Callable
from vk_scraper_imas.api.exceptions import VKAPIException
from .signals import *
import aiohttp


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
                        sys.stderr.write(f"HTTP POST завершился со статус кодом {response.status}")

        except aiohttp.ServerTimeoutError as ste:
            sys.stderr.write(str(ste))
        except aiohttp.ServerConnectionError as sce:
            sys.stderr.write(str(sce))
        except VKAPIException as vk_api_exc:
            sys.stderr.write(str(vk_api_exc))

    return wrapper


async def check_errors(response_json):
    if response_json.get('error'):
        error_code = response_json['error']['error_code']
        sys.stderr.write(str(VKAPIException(error_code)))

        if error_code == 29:
            return RateLimitSignal()
        if error_code == 30:
            return PrivateProfileSignal()

    return None

