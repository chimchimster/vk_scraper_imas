import pathlib
from dataclasses import dataclass


@dataclass
class Schemas:
    user_fields: pathlib.Path
    group_fields: pathlib.Path


@dataclass
class Connector:
    schemas: Schemas


schemas = Schemas(
    pathlib.Path('./api/schemas/user_fields.JSON'),
    pathlib.Path('./api/schemas/group_fields.JSON')
)

connector = Connector(schemas)
