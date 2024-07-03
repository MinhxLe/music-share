import os
from enum import Enum


class EnvType(str, Enum):
    LOCAL = "local"
    PROD = "prod"


ENV = os.getenv("ENV", EnvType.LOCAL)

match ENV:
    case EnvType.LOCAL:
        DB_URL = "localhost"
        DB_USER = "user"
        DB_PASSWORD = "password"
        DB_PORT = 5432
        DB_NAME = "postgres"
    case _:
        raise ValueError(f"not implemented env type {ENV}")
