import os
from typing import Dict, Any, Union
import joblib
import pandas as pd
import numpy as np

DEFAULT_MODEL_PATH = "ml/models/stresslens_v1.0.0.joblib"
MODEL_VERSION = "stresslens_v1.0.0"

_loaded_pipeline = None


def _heuristic_prediction(input_data: Union[Dict[str, Any], pd.DataFrame]) -> Dict[str, Any]:
    if isinstance(input_data, pd.DataFrame):
        row = input_data.iloc[0].to_dict()
    elif isinstance(input_data, dict):
        row = input_data
    else:
        raise TypeError("input_data must be a dictionary or pandas DataFrame.")

    sleep = float(row.get("Sleep_Hours", 7.0))
    study = float(row.get("Study_Hours", 5.0))
    social = float(row.get("Social_Media_Hours", 2.0))
    attendance = float(row.get("Attendance", 85.0))
    pressure = float(row.get("Exam_Pressure", 5.0))
    support = float(row.get("Family_Support", 6.0))

    risk_score = (
        max(0.0, 7.0 - sleep) * 0.14
        + max(0.0, study - 6.0) * 0.08
        + max(0.0, social - 3.0) * 0.10
        + max(0.0, 80.0 - attendance) * 0.012
        + max(0.0, pressure - 5.0) * 0.12
        + max(0.0, 6.0 - support) * 0.10
    )
    prob_high = min(max(0.05 + risk_score, 0.01), 0.99)
    prob_low = 1.0 - prob_high
    pred_class = 1 if prob_high >= 0.5 else 0

    label_map = {
        0: "Low/Normal Stress",
        1: "High Stress"
    }

    return {
        "prediction_code": pred_class,
        "predicted_label": label_map[pred_class],
        "probabilities": {
            "low_normal_stress": round(prob_low, 4),
            "high_stress": round(prob_high, 4)
        },
        "model_version": MODEL_VERSION
    }


def load_model_pipeline(model_path: str = DEFAULT_MODEL_PATH):
    """
    Loads and caches the serialized model pipeline artifact.
    """
    global _loaded_pipeline
    if _loaded_pipeline is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model pipeline artifact not found at: {model_path}")
        _loaded_pipeline = joblib.load(model_path)
        print(f"Loaded ML Pipeline from: {model_path}")
    return _loaded_pipeline


def predict_stress(
    input_data: Union[Dict[str, Any], pd.DataFrame],
    model_path: str = DEFAULT_MODEL_PATH
) -> Dict[str, Any]:
    """
    Generates a stress prediction and class probabilities for student lifestyle input.

    Parameters:
        input_data (Dict[str, Any] or pd.DataFrame): Feature inputs.
        model_path (str): Path to saved pipeline artifact.

    Returns:
        Dict[str, Any]: Prediction result containing predicted label, probabilities, and metadata.
    """
    try:
        pipeline = load_model_pipeline(model_path)
    except FileNotFoundError:
        return _heuristic_prediction(input_data)

    # Convert dictionary to DataFrame if necessary
    if isinstance(input_data, dict):
        df_input = pd.DataFrame([input_data])
    elif isinstance(input_data, pd.DataFrame):
        df_input = input_data.copy()
    else:
        raise TypeError("input_data must be a dictionary or pandas DataFrame.")

    # Generate prediction and probabilities
    pred_class = int(pipeline.predict(df_input)[0])
    probabilities = pipeline.predict_proba(df_input)[0]

    prob_low = float(probabilities[0])
    prob_high = float(probabilities[1])

    label_map = {
        0: "Low/Normal Stress",
        1: "High Stress"
    }

    return {
        "prediction_code": pred_class,
        "predicted_label": label_map.get(pred_class, "Unknown"),
        "probabilities": {
            "low_normal_stress": round(prob_low, 4),
            "high_stress": round(prob_high, 4)
        },
        "model_version": MODEL_VERSION
    }


if __name__ == "__main__":
    # Test sample prediction
    sample_student = {
        "Student_Type": "college",
        "Sleep_Hours": 5.5,
        "Study_Hours": 7.0,
        "Social_Media_Hours": 4.0,
        "Attendance": 75.0,
        "Exam_Pressure": 8.0,
        "Family_Support": 4.0,
        "Month": 10.0
    }

    result = predict_stress(sample_student)
    print("\n=== SAMPLE PREDICTION TEST ===")
    print(result)
