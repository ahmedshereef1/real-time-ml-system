import mlflow
import pandas as pd
from loguru import logger
from mlflow.models import infer_signature


def get_model_name(
    pair: str, candle_seconds: int, prediction_horizon_seconds: int
) -> str:
    """
    Returns the model name for the given pair and parameters.
    """
    return f'{pair}_{candle_seconds}_{prediction_horizon_seconds}'


def push_model(
    model,
    X_test: pd.DataFrame,
    model_name: str,
) -> None:
    """
    Push the given `model` to the model registry using the given `model_name`.

    Args:
        model: The model to push to the model regsitry.
        X_test: The test data to use for signature inference.
        model_name: The name to model to push to the model registry.
    """
    # Infer the model signature
    y_pred = model.predict(X_test)
    signature = infer_signature(X_test, y_pred)

    # Log the sklearn model and register as version 1
    logger.info(f'Pushing model {model_name} to the model registry')
    mlflow.sklearn.log_model(
        sk_model=model,
        name='model',
        signature=signature,
        registered_model_name=model_name,
    )
    logger.info(f'Model {model_name} pushed to the model registry')
