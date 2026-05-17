from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / '.env.local'),
        env_file_encoding='utf-8',
    )

    cryptocompare_api_key: str = Field(
        validation_alias=AliasChoices('CRYPTOCOMPARE_API_KEY', 'cryptocompare_api_key')
    )
    polling_interval_sec: int = Field(
        default=10,
        validation_alias=AliasChoices('POLLING_INTERVAL_SEC', 'polling_interval_sec'),
    )
    kafka_broker_address: str = Field(
        validation_alias=AliasChoices('KAFKA_BROKER_ADDRESS', 'kafka_broker_address')
    )
    kafka_output_topic: str = Field(
        validation_alias=AliasChoices('KAFKA_OUTPUT_TOPIC', 'kafka_output_topic')
    )


config = Settings()
