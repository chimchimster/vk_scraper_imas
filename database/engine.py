from vk_scraper_imas.database.config import config
from sqlalchemy.ext.asyncio import create_async_engine


class MySQLEngine:
    db_url = config.mysql_db.get_secret_value()
    engine = create_async_engine(db_url)


engine_mysql = MySQLEngine()
