def get_experiment_name(
    pair: str, candle_seconds: int, prediction_horizon_seconds: int
) -> str:
    """
    Returns the MLflow experiment name for the given pair and parameters.
    """
    return f'{pair}_{candle_seconds}_{prediction_horizon_seconds}'
