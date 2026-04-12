# Create an Application instance with Kafka configs
from loguru import logger
from quixstreams import Application

from trades.config import config
from trades.kraken_rest_api import KrakenRestAPI, KrakenRestMultiAPI
from trades.kraken_websocket_api import krakenWebsocketAPI
from trades.trade import Trade


def run(
    kafka_broker_address: str,
    kafka_topic_name: str,
    kraken_api: krakenWebsocketAPI | KrakenRestAPI | KrakenRestMultiAPI,
):
    app = Application(broker_address=kafka_broker_address)

    # Define a topic "my_topic" with JSON serialization
    topic = app.topic(name=kafka_topic_name, value_serializer='json')

    # Create a Producer instance
    with app.get_producer() as producer:
        while not kraken_api.is_done():
            # Define an event to be produced
            events: list[Trade] = kraken_api.get_trades()

            for event in events:
                # Serialize an event using the defined Topic
                message = topic.serialize(key=event.product_id, value=event.to_dict())

                # Produce a message into the Kafka topic
                producer.produce(topic=topic.name, value=message.value, key=message.key)
                # logger.info(f"Produced message to tpoic {topic.name}")
                logger.info(f'Trade {event.to_dict()} pushed to Kafa')

            # breakpoint()


if __name__ == '__main__':
    # Create object that can talk to kraken API and get us the trade data in real time
    if config.live_or_historical == 'live':
        logger.info('Using live data from Kraken API')
        api = krakenWebsocketAPI(product_ids=config.product_ids)

    elif config.live_or_historical == 'historical':
        logger.info('Using historical data from Kraken API for all configured products')
        api = KrakenRestMultiAPI(
            product_ids=config.product_ids,
            last_n_days=config.last_n_days,
        )
    else:
        raise ValueError(
            'Invalid value for live_or_historical. Must be "live" or "historical".'
        )

    run(
        # kafka_broker_address="localhost:31234",
        kafka_broker_address=config.kafka_broker_address,
        kafka_topic_name=config.kafka_topic_name,
        kraken_api=api,
    )
