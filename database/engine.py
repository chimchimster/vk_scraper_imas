from sqlalchemy.ext.asyncio import create_async_engine
from vk_scraper_imas.database.config import config


class MySQLEngine:
    db_url = config.mysql_db.get_secret_value()
    engine = create_async_engine(db_url, pool_size=50, max_overflow=10)


engine_mysql = MySQLEngine()
