import pathlib
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MySQLSettings(BaseSettings):
    mysql_db: SecretStr
    model_config = SettingsConfigDict(env_file=pathlib.Path.cwd() / 'database' / '.env', env_file_encoding='utf-8')


config = MySQLSettings()
