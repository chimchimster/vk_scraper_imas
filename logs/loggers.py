import aiohttp

from logging import Formatter
from aiologger import Logger

from .config import authorization


stream_logger = Logger.with_default_handlers(
    name='stream',
    level='DEBUG',
    formatter=Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S"
    ),
)


class TelegramLogger(Logger):

    token = authorization.vk_token.get_secret_value()
    chat_id = authorization.chat_id.get_secret_value()

    async def send_logs(self, message):

        url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={message}"

        async with aiohttp.ClientSession() as session:
            await session.get(url)


telegram_logger = TelegramLogger.with_default_handlers(
    name='telegram',
    level='CRITICAL',
)
