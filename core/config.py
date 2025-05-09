import secrets
from typing import Literal
from pydantic import Field, PostgresDsn, AmqpDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict()

    # general
    ENV: Literal["dev", "test", "prod"] = Field(
        default="dev"
    )
    # fastapi
    TITLE: str = "Gameserver API"
    SECRET_KEY: str = secrets.token_urlsafe(8)

    # db
    DB_URI: PostgresDsn = Field(
        default="postgres://root:postgres@db/root"
    )

    # rabbit
    RABBIT_URI: AmqpDsn = Field(
        default="amqp://guest:guest@mq/"
    )

    CI: bool = Field(
        default=False
    )

config = Config()
print(config.model_dump())
