from typing import List, Dict, Union

import json
import pathlib
import aiofiles


async def read_schema(path: pathlib.Path, key: str) -> Union[List, Dict]:
    async with aiofiles.open(path, 'r') as file:
        data = await file.read()
        return json.loads(data).get(key)
