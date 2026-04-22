import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
file_path = os.path.join(BASE_DIR, 'models_scores_with_default_hyperparameters.parquet')

df = pd.read_parquet(file_path)

print(df)

# The winnder is HuberRegressor
