from functools import wraps

from .session import AsyncSessionLocal

from vk_scraper_imas.logs import telegram_logger


def execute_transaction(coro):
    @wraps(coro)
    async def wrapper(*args, **kwargs):

        async with AsyncSessionLocal() as session:
            async with session.begin() as transaction:
                try:
                    result = await coro(*args, **kwargs, session=session)
                    await transaction.commit()
                    return result
                except Exception as e:
                    await transaction.rollback()
                    await telegram_logger.send_logs(e)

    return wrapper

