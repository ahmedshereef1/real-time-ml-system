import os

import pandas as pd


class BaselineModel:
    def __init__(self):
        """
        Provide initial parameters to initialize the model.
        """
        pass

    def fit(self, X, y):
        """
        Fit the model to the data.
        """
        pass

    def predict(self, X) -> pd.Series:
        """
        Predict the target variable.
        """
        return X['close']


def generate_lazy_predict_model_table(
    X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series
) -> pd.DataFrame:
    """
    Uses lazypredict to fit N models with default hyperparameters for the given
    (X_train, y_train), and evaluate them with (X_test, y_test)
    """

    from lazypredict.Supervised import LazyRegressor
    from sklearn.metrics import mean_absolute_error

    mlflow_tracking_uri = os.environ['MLFLOW_TRACKING_URI']
    del os.environ['MLFLOW_TRACKING_URI']

    reg = LazyRegressor(
        verbose=0, ignore_warnings=False, custom_metric=mean_absolute_error
    )
    models, _ = reg.fit(X_train, X_test, y_train, y_test)

    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri

    return models
