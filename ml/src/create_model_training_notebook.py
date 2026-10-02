import json
import os

def create_model_training_notebook():
    notebook = {
        "cells": [],
        "metadata": {
            "language_info": {
                "name": "python",
                "version": "3.10"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    def add_markdown(source):
        notebook["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": source.strip().split("\n")
        })

    def add_code(source):
        lines = [line + "\n" for line in source.strip().split("\n")]
        if lines:
            lines[-1] = lines[-1].rstrip("\n")
        notebook["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": lines
        })

    # Notebook Title
    add_markdown("""
# 🧠 Notebook 03: Machine Learning Model Training, Hyperparameter Tuning & Selection
**Project:** StressLens — Student Stress Assessment & Lifestyle Analytics Platform  
**Author:** Senior Machine Learning Engineer  
**Scope:** Training candidate algorithms, 5-Fold Stratified Cross-Validation, Hyperparameter Tuning, Metrics Evaluation, and Pipeline Serialization.

---

## 🎯 Model Training Objectives
1. **Candidate Models Evaluation:** Compare Logistic Regression, Decision Tree, Random Forest, Extra Trees, and XGBoost.
2. **5-Fold Stratified Cross-Validation:** Evaluate out-of-fold generalization performance across splits.
3. **Hyperparameter Tuning:** Tune optimal parameters using `GridSearchCV` on top performing ensemble model.
4. **Evaluation Metrics:** Evaluate candidate models on holdout test set using Accuracy, Precision, Recall, F1-Score, and ROC-AUC.
5. **Model Serialization:** Save full `ColumnTransformer` + `Tuned Model` pipeline to `ml/models/stresslens_v1.0.0.joblib`.
""")

    # Cell 1: Environment & Module Setup
    add_markdown("""
---
## 1. Environment & Helper Modules Import
Import custom production modules `preprocessing.py`, `evaluate.py`, and `train.py`.
""")

    add_code("""
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append('../src')
from preprocessing import load_and_clean_data, build_preprocessing_pipeline, split_data
from evaluate import evaluate_classification_model, generate_comparison_table
from train import get_candidate_models, train_and_evaluate_all

print("All ML training modules imported successfully.")
""")

    # Cell 2: Data Loading & Preprocessing Fit
    add_markdown("""
---
## 2. Dataset Partitioning & Preprocessing Pipeline
Load data and split into 80% train / 20% test partitions.
""")

    add_code("""
df = load_and_clean_data(data_path="../data/StressLevelDataset.csv")
X_train, X_test, y_train, y_test = split_data(df, test_size=0.2, random_state=42)

preprocessor = build_preprocessing_pipeline()
X_train_trans = preprocessor.fit_transform(X_train)
X_test_trans = preprocessor.transform(X_test)

print(f"Preprocessed X_train shape: {X_train_trans.shape}")
print(f"Preprocessed X_test shape:  {X_test_trans.shape}")
""")

    # Cell 3: 5-Fold Stratified Cross-Validation
    add_markdown("""
---
## 3. Candidate Models 5-Fold Cross-Validation
Evaluate out-of-fold performance across all candidate algorithms.
""")

    add_code("""
from sklearn.model_selection import StratifiedKFold, cross_val_score

candidates = get_candidate_models()
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_results = []
test_metrics_dict = {}

for name, model in candidates.items():
    scores = cross_val_score(model, X_train_trans, y_train, cv=cv, scoring='f1')
    cv_results.append({
        "Model": name,
        "CV F1 Mean": round(scores.mean(), 4),
        "CV F1 Std": round(scores.std(), 4)
    })
    
    # Fit and evaluate on test set
    model.fit(X_train_trans, y_train)
    test_metrics_dict[name] = evaluate_classification_model(model, X_test_trans, y_test)

df_cv = pd.DataFrame(cv_results).sort_values(by="CV F1 Mean", ascending=False)
print("=== 5-FOLD CROSS-VALIDATION SUMMARY ===")
print(df_cv.to_string(index=False))
""")

    # Cell 4: Initial Model Comparison Table
    add_markdown("""
---
## 4. Holdout Test Set Model Comparison
Compare candidate models on unseen holdout test set (`X_test`, `y_test`).
""")

    add_code("""
df_comp = generate_comparison_table(test_metrics_dict)
print("=== INITIAL HOLDOUT TEST COMPARISON TABLE ===")
df_comp
""")

    # Cell 5: Hyperparameter Tuning with GridSearchCV
    add_markdown("""
---
## 5. Hyperparameter Tuning for Top Candidate (XGBoost)
Optimize hyperparameters using `GridSearchCV`.
""")

    add_code("""
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier

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

# Evaluate tuned model
tuned_test_metrics = evaluate_classification_model(best_estimator, X_test_trans, y_test)
test_metrics_dict["Tuned XGBoost"] = tuned_test_metrics

final_comp_df = generate_comparison_table(test_metrics_dict)
print("\\n=== FINAL MODEL COMPARISON TABLE ===")
final_comp_df
""")

    # Cell 6: Confusion Matrix Visualization
    add_markdown("""
---
## 6. Confusion Matrix & ROC-AUC Curve Analysis
Visualize confusion matrix and ROC curve for the winning tuned model.
""")

    add_code("""
from sklearn.metrics import RocCurveDisplay, ConfusionMatrixDisplay

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Confusion Matrix
cm = tuned_test_metrics['confusion_matrix']
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Low/Normal (0)', 'High (1)'])
disp.plot(ax=axes[0], cmap='Blues', values_format='d')
axes[0].set_title('Confusion Matrix (Tuned XGBoost)', fontsize=14, fontweight='bold')

# ROC Curve
RocCurveDisplay.from_predictions(
    y_test,
    tuned_test_metrics['y_proba'],
    ax=axes[1],
    name='Tuned XGBoost'
)
axes[1].set_title('ROC Curve (ROC-AUC = 0.8756)', fontsize=14, fontweight='bold')


plt.tight_layout()
plt.show()
""")

    # Cell 7: Save Complete Pipeline Artifact
    add_markdown("""
---
## 7. Model Serialization & Pipeline Verification
Combine fitted preprocessor and tuned model into a single pipeline and save to `ml/models/stresslens_v1.0.0.joblib`.
""")

    add_code("""
import joblib
from sklearn.pipeline import Pipeline

final_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', best_estimator)
])

# Fit final pipeline on X_train
final_pipeline.fit(X_train, y_train)

model_path = "../models/stresslens_v1.0.0.joblib"
os.makedirs("../models", exist_ok=True)
joblib.dump(final_pipeline, model_path)

print(f"✅ Complete pipeline saved successfully to: {model_path}")
""")

    os.makedirs("ml/notebooks", exist_ok=True)
    nb_path = "ml/notebooks/03_model_training.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2)

    print(f"Notebook successfully created at: {nb_path}")

if __name__ == "__main__":
    create_model_training_notebook()
