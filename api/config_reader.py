from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    vk_token: SecretStr
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')


config = APISettings()
