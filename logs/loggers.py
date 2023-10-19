import aiohttp

from logging import Formatter
from aiologger.loggers.json import JsonLogger

from .config import authorization


stream_logger = JsonLogger.with_default_handlers(
    name='stream',
    serializer_kwargs={'ensure_ascii': False},
)


class TelegramLogger(JsonLogger):

    token = authorization.vk_token.get_secret_value()
    chat_id = authorization.chat_id.get_secret_value()

    async def send_logs(self, message):

        url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={message}"

        async with aiohttp.ClientSession() as session:
            await session.get(url)


telegram_logger = TelegramLogger.with_default_handlers(
    name='telegram',
    serializer_kwargs={'ensure_ascii': False},
)
