"""
The training script for the predictor service.

Has the following steps:
1. Fetch the data from Risingwace
2. Add target column
3. validate the data
4. Profile it
5. Split into train/test
6. Xgboost model with default hyperparameters
7. Validate final model
8. Push model
"""

import great_expectations as ge
import pandas as pd
from loguru import logger
from risingwave import OutputFormat, RisingWave, RisingWaveConnOptions


def validate_data(ts_data: pd.DataFrame) -> pd.DataFrame:
    """
    If the percentage of rows with missing values is greater than `max_percentage_rows_with_missing_values`,
    raise an exception so that the training process can be aborted.

    If that tests passes, check for the following things:

    - Column "close" has values more than 0
    # - Column "volume" has values more than 0
    # - Column "window_start_ms" is sorted

    """
    ge_df = ge.from_pandas(ts_data)

    validation_result = ge_df.expect_column_values_to_be_greater_than(
        column='close',
        min_value=0,
    )

    if not validation_result.success:
        raise Exception('Column "close" has values less than 0')

    # TODO: Add more validation checks
    # For example:
    # - Check for null values
    # - Check for duplicates
    # - Check the data is sorted by timestamp
    # - ...

    return ts_data


def load_ts_data_from_risingwave(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    table: str,
    pair: str,
    training_data_horizon_days: int,
    candle_seconds: int,
) -> pd.DataFrame:
    """
    Fetches technical indicators data from RisingWave for the given pair and time range.

    Args:
        host: str: The host of the RisingWave instance.
        port: int: The port of the RisingWave instance.
        user: str: The user to connect to RisingWave.
        password: str: The password to connect to RisingWave.
        database: str: The database to connect to RisingWave.
        pair: str: The trading pair to fetch data for.
        training_data_horizon_days: int: The number of days in the past to fetch data for.
        candle_seconds: int: The candle duration in seconds.

    Returns:
        pd.DataFrame: A DataFrame containing the technical indicators data for the given pair.
    """
    logger.info('Establishing connection to RisingWave')
    rw = RisingWave(
        RisingWaveConnOptions.from_connection_info(
            host=host, port=port, user=user, password=password, database=database
        )
    )

    query = f"""
    select
        *
    from
        {table}
    where
        pair='{pair}'
        and candle_seconds='{candle_seconds}'
        and to_timestamp(window_start_ms / 1000) > now() - interval '{training_data_horizon_days} days'
    order by
        window_start_ms;
    """

    ts_data = rw.fetch(query, format=OutputFormat.DATAFRAME)

    logger.info(
        f'Fetched {len(ts_data)} rowsof data for {pair} in the last {training_data_horizon_days} days from Risingwave'
    )

    return ts_data


def train(
    risingwave_host: str,
    risingwave_port: int,
    risingwave_user: str,
    risingwave_password: str,
    risingwave_database: str,
    risingwave_table: str,
    pair: str,
    training_data_horizon_days: int,
    candle_seconds: int,
    prediction_horizon_seconds: int,
):
    """
    Trains a predictor for the given pair and data, and if the model is good, it pushes
    it to the model registry.
    """
    logger.info('Starting training process')

    # Step 1: Fetch the data from Risingwace
    ts_data = load_ts_data_from_risingwave(
        host=risingwave_host,
        port=risingwave_port,
        user=risingwave_user,
        password=risingwave_password,
        database=risingwave_database,
        table=risingwave_table,
        pair=pair,
        training_data_horizon_days=training_data_horizon_days,
        candle_seconds=candle_seconds,
    )

    # Step 2: Add target column
    ts_data['target'] = ts_data['close'].shift(
        -prediction_horizon_seconds // candle_seconds
    )

    # Step 3: validate the data
    validate_data(ts_data)

    # Step 4: Profile the data


if __name__ == '__main__':
    train(
        risingwave_host='localhost',
        risingwave_port=4567,
        risingwave_user='root',
        risingwave_password='',
        risingwave_database='dev',
        risingwave_table='technical_indicators',
        pair='BTC/USD',
        training_data_horizon_days=30,
        candle_seconds=60,
        prediction_horizon_seconds=300,
    )
