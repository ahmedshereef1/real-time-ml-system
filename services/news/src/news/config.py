from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    coinmarketcap_api_key: str
    polling_interval_sec: int = 10
    kafka_broker_address: str
    kafka_output_topic: str

    class Config:
        env_file = '.env.local'


config = Settings()
