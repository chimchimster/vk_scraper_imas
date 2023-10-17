import pathlib
from dataclasses import dataclass


@dataclass
class Schemas:
    user_fields: pathlib.Path
    group_fields: pathlib.Path
    path_to_tokens: pathlib.Path
    rate_limited: pathlib.Path


@dataclass
class Connector:
    schemas: Schemas


@dataclass
class TokenStorage:
    path_to_tokens: pathlib.Path = pathlib.Path('vk_scraper_imas') / 'scarper' / 'token' / 'schemas' / 'tokens.JSON'


schemas = Schemas(
    pathlib.Path('vk_scraper_imas') / 'api' / 'schemas' / 'user_fields.JSON',
    pathlib.Path('vk_scraper_imas') / 'api' / 'schemas' / 'group_fields.JSON',
    pathlib.Path('vk_scraper_imas') / 'scarper' / 'token' / 'schemas' / 'tokens.JSON',
    pathlib.Path('vk_scraper_imas') / 'scarper' / 'token' / 'schemas' / 'rate_limited.JSON'
)

connector = Connector(schemas)
