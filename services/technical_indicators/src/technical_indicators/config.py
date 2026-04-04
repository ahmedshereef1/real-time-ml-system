from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='services/technical_indicators/settings.env', env_file_encoding='utf-8'
    )

    kafka_broker_address: str = Field(
        validation_alias=AliasChoices('KAFKA_BROKER_ADDRESS', 'kafka_broker_address')
    )
    kafka_input_topic: str = Field(
        validation_alias=AliasChoices('KAFKA_INPUT_TOPIC', 'kafka_input_topic')
    )
    kafka_output_topic: str = Field(
        validation_alias=AliasChoices('KAFKA_OUTPUT_TOPIC', 'kafka_output_topic')
    )
    kafka_consumer_group: str = Field(
        validation_alias=AliasChoices('KAFKA_CONSUMER_GROUP', 'kafka_consumer_group')
    )
    candle_seconds: int = Field(
        validation_alias=AliasChoices('CANDLE_SECONDS', 'candle_seconds')
    )

    max_candles_in_state: int = Field(
        validation_alias=AliasChoices('MAX_CANDLES_IN_STATE', 'max_candles_in_state'),
        default=70,
    )

    # TODO: if you prefer, do not set a default value for this field
    table_name_in_risingwave: str = 'technical_indicators'


config = Settings()
