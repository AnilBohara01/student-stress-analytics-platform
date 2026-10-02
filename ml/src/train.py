import os
from typing import Dict, Any, Tuple
import joblib
import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier

from preprocessing import load_and_clean_data, build_preprocessing_pipeline, split_data
from evaluate import evaluate_classification_model, generate_comparison_table

MODEL_SAVE_DIR = "ml/models"
MODEL_VERSION = "stresslens_v1.0.0"
FINAL_MODEL_PATH = os.path.join(MODEL_SAVE_DIR, f"{MODEL_VERSION}.joblib")


def get_candidate_models() -> Dict[str, Any]:
    """
    Returns candidate models for evaluation.
    """
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=10, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "Extra Trees": ExtraTreesClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "XGBoost": XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42, eval_metric='logloss')
    }




def train_and_evaluate_all() -> Tuple[Pipeline, pd.DataFrame, Dict[str, Any]]:
    """
    Runs full training workflow: data loading, preprocessing, candidate model training,
    5-fold cross-validation, hyperparameter tuning, model evaluation, selection, and serialization.

    Returns:
        Tuple[Pipeline, pd.DataFrame, Dict[str, Any]]: Best combined pipeline, comparison DataFrame, and test metrics.
    """
    print("=== PHASE 4: ML MODEL TRAINING PIPELINE ===")

    # 1. Load and Split Data
    df = load_and_clean_data()
    X_train, X_test, y_train, y_test = split_data(df)

    # 2. Build and fit preprocessor on training set
    preprocessor = build_preprocessing_pipeline()
    X_train_trans = preprocessor.fit_transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    # 3. Cross-Validation Evaluation of Candidates
    candidates = get_candidate_models()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    cv_summary = {}
    test_results = {}

    print("\n--- 5-Fold Stratified Cross-Validation Results ---")
    for name, model in candidates.items():
        scores = cross_val_score(model, X_train_trans, y_train, cv=cv, scoring='f1')
        cv_summary[name] = {"cv_f1_mean": scores.mean(), "cv_f1_std": scores.std()}
        print(f"[{name}] 5-Fold CV F1-Score: {scores.mean():.4f} (+/- {scores.std():.4f})")

        # Fit model on training set and evaluate on test set
        model.fit(X_train_trans, y_train)
        test_results[name] = evaluate_classification_model(model, X_test_trans, y_test)

    # Display initial comparison
    comp_df = generate_comparison_table(test_results)
    print("\n--- Candidate Models Test Evaluation ---")
    print(comp_df.to_string(index=False))

    # 4. Hyperparameter Tuning for Top Model (XGBoost / Random Forest)
    print("\n--- Performing Hyperparameter Tuning on Top Candidate (XGBoost) ---")
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.05, 0.1, 0.2],
        'subsample': [0.8, 1.0]
    }

    xgb_base = XGBClassifier(random_state=42, eval_metric='logloss')
    grid_search = GridSearchCV(
        estimator=xgb_base,
        param_grid=param_grid,
        cv=cv,
        scoring='f1',
        n_jobs=-1,
        verbose=1
    )
    grid_search.fit(X_train_trans, y_train)

    best_estimator = grid_search.best_estimator_
    print(f"Best Parameters: {grid_search.best_params_}")
    print(f"Best CV F1-Score: {grid_search.best_score_:.4f}")

    # Evaluate Tuned Model on Test Set
    tuned_metrics = evaluate_classification_model(best_estimator, X_test_trans, y_test)
    test_results["Tuned XGBoost"] = tuned_metrics
    final_comp_df = generate_comparison_table(test_results)

    print("\n--- Final Model Comparison Table ---")
    print(final_comp_df.to_string(index=False))

    # 5. Build Final Combined Pipeline (Preprocessor + Best Estimator)
    final_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', best_estimator)
    ])

    # Re-fit final pipeline on full training data
    final_pipeline.fit(X_train, y_train)

    # 6. Save Pipeline Artifact
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    joblib.dump(final_pipeline, FINAL_MODEL_PATH)
    print(f"\n✅ Final Model Pipeline serialized successfully to: {FINAL_MODEL_PATH}")

    return final_pipeline, final_comp_df, tuned_metrics


if __name__ == "__main__":
    train_and_evaluate_all()
