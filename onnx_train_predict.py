"""Onnx runtime utils."""

import math
from pathlib import Path

import joblib
import numpy as np
from onnx import ModelProto
from onnxruntime import InferenceSession
from polars import DataFrame
from skl2onnx import convert_sklearn

from skl2onnx.common.data_types import Int64TensorType

from data_science import get_linear_regression_model


def train_model(
    df: DataFrame, sklearn_model_path: Path, model_path: Path, dump_sklearn: bool = True
) -> ModelProto:
    sklearn_model = get_linear_regression_model(df)

    # Dump to cache (for analysis in jupyter notebook)
    if dump_sklearn:
        joblib.dump(sklearn_model, sklearn_model_path)

    # Set the initial type for the ONNX model: [None, number_of_features]
    n_features = df.select("population").shape[1]
    initial_type = [("population", Int64TensorType([None, n_features]))]

    # Convert and return the model
    onnx_model = convert_sklearn(sklearn_model, initial_types=initial_type)

    with open(model_path, "wb") as f:
        f.write(onnx_model.SerializeToString())

    # Todo: read from in-memory model instead
    return InferenceSession(model_path)


def predict(session: InferenceSession, population: int):
    """
    Predict visitors per year using the ONNX model.

    Args:
        session: ONNX session
        population: Given city population

    Returns:
        Predicted number of visitors per year in a museum
    """
    x_input = np.array([[population]])
    output = session.run(None, {"population": x_input})

    return math.floor(float(output[0][0][0]))
