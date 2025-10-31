"""Model builder with pure ONNX"""

import math

import numpy as np
import polars as pl
from sklearn.linear_model import LinearRegression
from onnx import ModelProto
from onnxruntime import InferenceSession
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import Int64TensorType


def get_linear_regression_model(df: pl.DataFrame) -> ModelProto:
    """
    Complete pipeline: train model, create ONNX graph, and save.

    Args:
        df: Polars DataFrame with training data

    Returns:
        ONNX model
    """
    arrays = df.select("population", "avg_museum_visitors_per_year").to_numpy()
    x = np.expand_dims(arrays[:, 0], 1)
    y = arrays[:, 1]

    # Create and train the model
    model = LinearRegression()
    model.fit(x, y)

    # Define the input type and shape for the ONNX model
    # The shape is [None, number_of_features] (None means dynamic batch size)
    initial_type = [("population", Int64TensorType([None, x.shape[1]]))]

    # Convert the model
    onnx_model = convert_sklearn(model, initial_types=initial_type)
    return onnx_model


def predict(session: InferenceSession, population: int):
    """
    Predict visitors per year using the ONNX model.

    Args:
        session: ONNX session
        population: City population

    Returns:
        Predicted number of visitors per year
    """
    x_input = np.array([[population]])
    output = session.run(None, {"population": x_input})

    return math.floor(float(output[0][0][0]))
