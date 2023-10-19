import pathlib
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class VKAuthorizeSettings(BaseSettings):
    vk_token: SecretStr
    chat_id: SecretStr
    model_config = SettingsConfigDict(env_file=pathlib.Path.cwd() / 'logs' / '.env', env_file_encoding='utf-8')


authorization = VKAuthorizeSettings()