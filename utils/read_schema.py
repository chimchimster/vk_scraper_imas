import json
import pathlib
import aiofiles


async def read_schema(path: pathlib.Path) -> json:
    async with aiofiles.open(path, 'r') as file:
        data = await file.read()
        return json.loads(data)
