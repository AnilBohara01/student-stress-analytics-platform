import os
from typing import Dict, Any, List, Union
import joblib
import pandas as pd
import numpy as np
import shap

try:
    from predict import load_model_pipeline, DEFAULT_MODEL_PATH
except ImportError:
    from ml.src.predict import load_model_pipeline, DEFAULT_MODEL_PATH


_cached_explainer = None


def get_shap_explainer(pipeline=None, model_path: str = DEFAULT_MODEL_PATH):
    """
    Returns cached SHAP TreeExplainer for the pipeline's XGBoost model.
    """
    global _cached_explainer
    if _cached_explainer is None:
        if pipeline is None:
            pipeline = load_model_pipeline(model_path)
        model = pipeline.named_steps['model']
        _cached_explainer = shap.TreeExplainer(model)
        print("Initialized SHAP TreeExplainer.")
    return _cached_explainer


def get_feature_names(preprocessor) -> List[str]:
    """
    Extracts ordered feature names from fitted ColumnTransformer.
    """
    num_cols = ['Sleep_Hours', 'Study_Hours', 'Social_Media_Hours', 'Attendance', 'Exam_Pressure', 'Family_Support', 'Month']
    cat_cols = list(preprocessor.named_transformers_['cat'].named_steps['encoder'].get_feature_names_out(['Student_Type']))
    return num_cols + cat_cols


def explain_prediction(
    input_data: Union[Dict[str, Any], pd.DataFrame],
    model_path: str = DEFAULT_MODEL_PATH,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Computes SHAP feature attributions for a given student input and returns human-readable explanations.

    Parameters:
        input_data: Feature input dictionary or DataFrame.
        model_path: Path to serialized pipeline artifact.
        top_k: Number of top contributing factors to highlight.

    Returns:
        Dict[str, Any]: SHAP explanation breakdown including top factors and summary narrative.
    """
    pipeline = load_model_pipeline(model_path)
    preprocessor = pipeline.named_steps['preprocessor']

    if isinstance(input_data, dict):
        df_input = pd.DataFrame([input_data])
    else:
        df_input = input_data.copy()

    # Preprocess input
    X_trans = preprocessor.transform(df_input)
    feature_names = get_feature_names(preprocessor)

    # Calculate SHAP values
    explainer = get_shap_explainer(pipeline, model_path)
    shap_vals = explainer(X_trans)
    values = shap_vals.values[0]

    # Map features to readable labels and values
    feature_impacts = []
    for name, shap_val in zip(feature_names, values):
        readable_name = name.replace("Student_Type_", "Student Category: ").replace("_", " ")
        feature_impacts.append({
            "feature_raw": name,
            "feature_label": readable_name,
            "shap_value": float(shap_val),
            "impact_direction": "increases_stress" if shap_val > 0 else "decreases_stress",
            "abs_impact": float(abs(shap_val))
        })

    # Sort by absolute impact
    feature_impacts.sort(key=lambda x: x["abs_impact"], reverse=True)
    top_factors = feature_impacts[:top_k]

    # Generate non-clinical narrative summary
    increasing_factors = [f["feature_label"] for f in top_factors if f["shap_value"] > 0]
    decreasing_factors = [f["feature_label"] for f in top_factors if f["shap_value"] < 0]

    narrative_parts = []
    if increasing_factors:
        narrative_parts.append(f"Factors associated with higher predicted stress: {', '.join(increasing_factors)}.")
    if decreasing_factors:
        narrative_parts.append(f"Factors supporting stress reduction: {', '.join(decreasing_factors)}.")

    summary_text = " ".join(narrative_parts) if narrative_parts else "Feature levels aligned with balanced stress indicators."

    return {
        "top_contributing_factors": top_factors,
        "all_feature_impacts": feature_impacts,
        "narrative_explanation": summary_text
    }


if __name__ == "__main__":
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

    explanation = explain_prediction(sample_student)
    print("\n=== SHAP EXPLAINABILITY TEST ===")
    print("Narrative Explanation:", explanation["narrative_explanation"])
    print("\nTop Factors:")
    for factor in explanation["top_contributing_factors"]:
        print(f" - {factor['feature_label']}: SHAP={factor['shap_value']:+.4f} ({factor['impact_direction']})")
