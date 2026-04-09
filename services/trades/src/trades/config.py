from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='services/trades/settings.env', env_file_encoding='utf-8'
    )

    product_ids: list[str] = [
        'ETH/EUR',
        'BTC/USD',
        'BTC/EUR',
        'ETH/USD',
        'SOL/USD',
        'SOL/EUR',
        'XRP/USD',
        'XRP/EUR',
    ]
    kafka_broker_address: str = Field(
        validation_alias=AliasChoices('KAFKA_BROKER_ADDRESS', 'kafka_broker_address')
    )
    kafka_topic_name: str = Field(
        validation_alias=AliasChoices(
            'KAFKA_TOPIC_NAME',
            'KAFKA_TOPIC',
            'kafka_topic_name',
        )
    )
    live_or_historical: Literal['live', 'historical'] = 'live'
    last_n_days: int = 30


config = Settings()
