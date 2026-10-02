from typing import Dict, Any
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


def evaluate_classification_model(model: Any, X_test: np.ndarray, y_test: pd.Series) -> Dict[str, Any]:
    """
    Evaluates a trained classifier on test dataset and computes key classification metrics.

    Parameters:
        model: Trained model or pipeline.
        X_test: Preprocessed feature matrix for testing.
        y_test: Ground truth labels.

    Returns:
        Dict[str, Any]: Dictionary containing metric values and confusion matrix.
    """
    y_pred = model.predict(X_test)

    # Probabilities for ROC-AUC (if supported)
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)[:, 1]
    elif hasattr(model, "decision_function"):
        y_proba = model.decision_function(X_test)
    else:
        y_proba = y_pred

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(roc_auc),
        "confusion_matrix": cm,
        "y_pred": y_pred,
        "y_proba": y_proba
    }


def generate_comparison_table(results_dict: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """
    Creates a formatted comparison table from model evaluation results.

    Parameters:
        results_dict: Dictionary mapping model names to metric dictionaries.

    Returns:
        pd.DataFrame: Sorted comparison DataFrame.
    """
    rows = []
    for model_name, metrics in results_dict.items():
        rows.append({
            "Model": model_name,
            "Accuracy": round(metrics["accuracy"], 4),
            "Precision": round(metrics["precision"], 4),
            "Recall": round(metrics["recall"], 4),
            "F1-Score": round(metrics["f1_score"], 4),
            "ROC-AUC": round(metrics["roc_auc"], 4)
        })

    df_comp = pd.DataFrame(rows).sort_values(by="F1-Score", ascending=False).reset_index(drop=True)
    return df_comp
