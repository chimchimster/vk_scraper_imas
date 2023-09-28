import json
import sys
from functools import wraps
from typing import Awaitable, Optional, Callable
from vk_scraper_imas.api.exceptions import VKAPIException
import aiohttp


def do_post_request_to_vk_api(func: Optional[Callable[..., Awaitable[None]]]):
    @wraps(func)
    async def wrapper(*args, **kwargs):

        request_string = await func(*args, **kwargs)

        try:
            async with aiohttp.ClientSession(
                    json_serialize=json.dumps,
            ) as session:
                async with session.post(request_string) as response:
                    if response.status == 200:
                        response_str = await response.text()
                        response_json = json.loads(response_str)

                        await check_errors(response_json)

                        return response_json
                    else:
                        sys.stderr.write(f"HTTP POST завершился со статус кодом {response.status}")

        except VKAPIException as vk_api_exc:
            sys.stderr.write(str(vk_api_exc))

    return wrapper


async def check_errors(response_json):
    if response_json.get('error'):
        error_code = response_json['error']['error_code']
        sys.stderr.write(str(VKAPIException(error_code)))
