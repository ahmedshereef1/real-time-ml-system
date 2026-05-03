import great_expectations as ge
import pandas as pd


def validate_data(
    ts_data: pd.DataFrame, max_percentage_rows_with_missing_values: float
) -> pd.DataFrame:
    """
    If the percentage of rows with missing values is greater than `max_percentage_rows_with_missing_values`,
    raise an exception so that the training process can be aborted.

    If that tests passes, check for the following things:

    - Column "close" has values more than 0
    # - Column "volume" has values more than 0
    # - Column "window_start_ms" is sorted

    """
    # Check for missing values
    ts_data_without_nans = ts_data.dropna()
    perc_rows_with_missing_data = (len(ts_data) - len(ts_data_without_nans)) / len(
        ts_data
    )

    if perc_rows_with_missing_data > max_percentage_rows_with_missing_values:
        raise Exception(
            'ts_data has too many rows with missing data. Aborting the training script.'
        )

    ts_data = ts_data_without_nans

    # Then the reset of the checks
    ge_df = ge.from_pandas(ts_data)

    validation_result = ge_df.expect_column_values_to_be_between(
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
