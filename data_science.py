"""Model builder with pure ONNX"""

import numpy as np

try:
    from polars import DataFrame
except ModuleNotFoundError:
    from pandas import DataFrame

from sklearn.linear_model import LinearRegression


def get_linear_regression_model(df: DataFrame) -> LinearRegression:
    """
    Train and return a sklearn linear regression model.

    Args:
        df: DataFrame with training data

    Returns:
        Trained sklearn linear regression model
    """
    try:
        arrays = df.select("population", "avg_museum_visitors_per_year").to_numpy()
    except AttributeError:
        # fallback to pandas
        arrays = df[["population", "avg_museum_visitors_per_year"]].to_numpy()

    # Create the training arrays
    x = np.expand_dims(arrays[:, 0], 1)
    y = arrays[:, 1]

    # Create and train the model
    model = LinearRegression()
    model.fit(x, y)

    return model
