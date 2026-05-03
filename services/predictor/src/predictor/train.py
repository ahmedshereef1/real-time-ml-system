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

from typing import Optional

import mlflow
import pandas as pd
from loguru import logger
from risingwave import OutputFormat, RisingWave, RisingWaveConnOptions
from sklearn.metrics import mean_absolute_error
from ydata_profiling import ProfileReport

from predictor.data_validation import validate_data
from predictor.model_registry import get_model_name, push_model
from predictor.models import BaselineModel, get_model_candidates, get_model_obj


def generate_exploratory_data_analysis_report(
    ts_data: pd.DataFrame,
    output_html_path: str,
):
    """
    Genearates an HTML file exploratory data analysis charts for the given `ts_data` and
    saves it locally to the given `output_html_path`

    Args:
        ts_data: The DataFrame containing the technical indicators data.
        output_html_file: The path to save the HTML report.
    """

    profile = ProfileReport(
        ts_data, tsmode=True, sortby='window_start_ms', title='Technical indicators EDA'
    )
    profile.to_file(output_html_path)


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
    mlflow_tracking_uri: str,
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
    train_test_split_ratio: float,
    max_percentage_rows_with_missing_values: float,
    n_rows_for_data_profiling: int,
    eda_report_html_path: str,
    features: list[str],
    hyperparam_search_trials: int,
    model_name: Optional[str] = None,
    n_model_candidates: Optional[int] = 1,
    max_percentage_diff_mae_wrt_baseline: Optional[float] = 0.10,
):
    """
    Trains a predictor for the given pair and data, and if the model is good, it pushes
    it to the model registry.
    """
    logger.info('Starting training process')

    logger.info('Setting up MLflow tracking URI')
    mlflow.set_tracking_uri(mlflow_tracking_uri)

    logger.info('Setting up MLflow experiment')
    from predictor.names import get_experiment_name

    mlflow.set_experiment(
        get_experiment_name(pair, candle_seconds, prediction_horizon_seconds)
    )

    # Things we want to log to MLflow:
    # - The data we used to train the model
    # - Parameters
    # - EDA report
    # - Model performance metrics

    with mlflow.start_run():
        logger.info('Starting MLflow run')

        # Input to the Training process
        mlflow.log_param('features', features)
        mlflow.log_param('pair', pair)
        mlflow.log_param('candle_seconds', candle_seconds)
        mlflow.log_param('prediction_horizon_seconds', prediction_horizon_seconds)
        mlflow.log_param('data_horizon_days', training_data_horizon_days)
        mlflow.log_param('train_test_split_ratio', train_test_split_ratio)
        mlflow.log_param('n_rows_for_data_profiling', n_rows_for_data_profiling)
        mlflow.log_param(
            'max_percentage_diff_mae_wrt_baseline', max_percentage_diff_mae_wrt_baseline
        )
        if model_name:
            mlflow.log_param('model_name', model_name)

        # Step 1:  Load technical indicators data from RisingWave
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

        # Keep only the features we need and the target column
        ts_data = ts_data[features]

        # Step 2: Add target column
        ts_data['target'] = ts_data['close'].shift(
            -prediction_horizon_seconds // candle_seconds
        )

        # TAKE ONLY 1/2 OF DATA (FAST DEV MODE)
        ts_data = ts_data.iloc[: len(ts_data) // 2]

        # log the data to MLflow
        dataset = mlflow.data.from_pandas(ts_data)
        mlflow.log_input(dataset, context='training')

        # log dataset size
        mlflow.log_param('ts_data_shape', ts_data.shape)

        # Step 3: validate the data
        ts_data = validate_data(ts_data, max_percentage_rows_with_missing_values)

        # Step 4: Profile the data
        ts_data_for_profile = (
            ts_data.head(n_rows_for_data_profiling)
            if n_rows_for_data_profiling
            else ts_data
        )
        generate_exploratory_data_analysis_report(
            ts_data_for_profile, output_html_path=eda_report_html_path
        )

        logger.info('Publishing EDA report to MLflow')
        mlflow.log_artifact(local_path=eda_report_html_path, artifact_path='eda_report')

        # Step 5: Split into train/test
        train_size = int(len(ts_data) * train_test_split_ratio)
        train_data = ts_data[:train_size]
        test_data = ts_data[train_size:]
        mlflow.log_param('train_data_shape', train_data.shape)
        mlflow.log_param('test_data_shape', test_data.shape)

        # Step 6: Split data into features and target
        X_train = train_data.drop(columns=['target'])
        y_train = train_data['target']
        X_test = test_data.drop(columns=['target'])
        y_test = test_data['target']
        mlflow.log_param('X_train_shape', X_train.shape)
        mlflow.log_param('y_train_shape', y_train.shape)
        mlflow.log_param('X_test_shape', X_test.shape)
        mlflow.log_param('y_test_shape', y_test.shape)

        # Step 7: Build a dummy baseline model
        baseline_model = BaselineModel()
        y_pred = baseline_model.predict(X_test)
        test_mae_baseline = mean_absolute_error(y_test, y_pred)
        mlflow.log_metric('test_mae_baseline', test_mae_baseline)
        logger.info(f'Baseline model test MAE: {test_mae_baseline:.4f}')

        # Step 8: Find the best candidate model, if `model_name` is not provided.
        if model_name is None:
            # We fit N models with default hyperparameters for the given
            # (X_train, y_train), and evaluate them with (X_test, y_test)
            # to find the best `n_model_candidates` models
            model_names = get_model_candidates(
                X_train, y_train, X_test, y_test, n_candidates=n_model_candidates
            )
            mlflow.log_param('model_candidates', model_names)
            model_name = model_names[0]

        model = get_model_obj(model_name)

        # Step 9: Train the choosen model with hyperparameter search.
        logger.info(f'Start training model: {model} with hyperparameter search')
        model.fit(X_train, y_train, hyperparam_search_trials=hyperparam_search_trials)

        # Step 10: Validate the model
        y_pred = model.predict(X_test)
        test_mae = mean_absolute_error(y_test, y_pred)
        mlflow.log_metric('test_mae', test_mae)
        logger.info(f'Test MAE for model {model}: {test_mae:.4f}')

        # Step 11: Push the model to the model registry
        if (
            test_mae - test_mae_baseline
        ) / test_mae_baseline <= max_percentage_diff_mae_wrt_baseline:
            logger.info(
                f'Model MAE is within {max_percentage_diff_mae_wrt_baseline} perc difference.'
            )
            logger.info('Pushing model to the model registry')
            model_name = get_model_name(
                pair, candle_seconds, prediction_horizon_seconds
            )
            push_model(model, X_test, model_name)
        else:
            logger.info(f'The model {model_name} has an MAE too far from the baseline')
            logger.info('Model NOT PUSHED to the model registry')


if __name__ == '__main__':
    train(
        mlflow_tracking_uri='http://127.0.0.1:8283',
        risingwave_host='localhost',
        risingwave_port=4567,
        risingwave_user='root',
        risingwave_password='',
        risingwave_database='dev',
        risingwave_table='technical_indicators',
        pair='BTC/USD',
        training_data_horizon_days=10,
        candle_seconds=60,
        prediction_horizon_seconds=300,
        train_test_split_ratio=0.8,
        max_percentage_rows_with_missing_values=0.01,  # data quality check
        n_rows_for_data_profiling=1,  # TODO: set to 1 to speed up development
        eda_report_html_path='./eda_report.html',
        features=[
            'open',
            'high',
            'low',
            'close',
            'window_start_ms',
            'volume',
            'sma_7',
            'sma_14',
            'sma_21',
            'sma_60',
            'ema_7',
            'ema_14',
            'ema_21',
            'ema_60',
            'rsi_7',
            'rsi_14',
            'rsi_21',
            'rsi_60',
            'macd_7',
            'macdsignal_7',
            'macdhist_7',
            'obv',
        ],
        hyperparam_search_trials=10,
        model_name='HuberRegressor',
        n_model_candidates=1,
        # only push the model if it improves the MAE by at least 10% compared to the baseline model
        # In a real scenario you can reduce this parameter further
        max_percentage_diff_mae_wrt_baseline=0.10,
    )

# direnv exec . uv run src/predictor/train.py
