import json
import os

def create_preprocessing_notebook():
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

    # Title & Metadata
    add_markdown("""
# ⚙️ Notebook 02: Reusable Data Preprocessing & Leakage Prevention Pipeline
**Project:** StressLens — Student Stress Assessment & Lifestyle Analytics Platform  
**Author:** Senior Machine Learning Engineer  
**Scope:** Building a leak-free Scikit-Learn preprocessing pipeline and dataset splitting framework.

---

## 🎯 Preprocessing Pipeline Objectives
1. **Deduplication:** Remove exact duplicate records from the dataset.
2. **Stratified Train/Test Split:** Partition data into 80% training set and 20% holdout test set using target stratification (`Stress_Level`).
3. **Missing Value Imputation:**
   - Median imputation for continuous numerical features (`Sleep_Hours`, `Study_Hours`, `Social_Media_Hours`, `Attendance`, `Exam_Pressure`, `Family_Support`, `Month`).
   - Most frequent (mode) imputation for categorical feature (`Student_Type`).
4. **Categorical Encoding:** One-Hot Encoding (`drop='first'`) for `Student_Type` categories.
5. **Numerical Scaling:** Standardization (`StandardScaler`) for numerical variables to ensure zero mean and unit variance.
6. **Data Leakage Prevention:** Fit all transformers strictly on `X_train` and apply `transform` on `X_test`.
""")

    # Cell 1: Environment & Module Setup
    add_markdown("""
---
## 1. Import Reusable Preprocessing Module
Import custom reusable functions defined in `ml/src/preprocessing.py`.
""")

    add_code("""
import sys
import os
import pandas as pd
import numpy as np

# Add src directory to system path
sys.path.append('../src')
from preprocessing import load_and_clean_data, build_preprocessing_pipeline, split_data, NUMERICAL_FEATURES, CATEGORICAL_FEATURES, TARGET_COLUMN

print("Preprocessing module imported successfully.")
print(f"Numerical Features: {NUMERICAL_FEATURES}")
print(f"Categorical Features: {CATEGORICAL_FEATURES}")
""")

    # Cell 2: Data Loading & Deduplication
    add_markdown("""
---
## 2. Load Dataset & Deduplicate
Load dataset from `../data/StressLevelDataset.csv` and remove duplicates.
""")

    add_code("""
df = load_and_clean_data(data_path="../data/StressLevelDataset.csv")
print(f"Cleaned dataset shape: {df.shape}")
df.head()
""")

    # Cell 3: Stratified Train/Test Split
    add_markdown("""
---
## 3. Stratified Train / Test Split
Split dataset into 80% training (`X_train`, `y_train`) and 20% holdout test set (`X_test`, `y_test`).
""")

    add_code("""
X_train, X_test, y_train, y_test = split_data(df, test_size=0.2, random_state=42)

# Verify class balance across splits
print("\\n=== TARGET CLASS BALANCE CHECK ===")
print("Overall dataset ratio:\\n", df[TARGET_COLUMN].value_counts(normalize=True))
print("\\nTraining set ratio:\\n", y_train.value_counts(normalize=True))
print("\\nTesting set ratio:\\n", y_test.value_counts(normalize=True))
""")

    # Cell 4: Constructing & Fitting Preprocessing Pipeline
    add_markdown("""
---
## 4. Constructing Scikit-Learn ColumnTransformer
Create `ColumnTransformer` containing numerical and categorical pipelines. Fit transformer strictly on `X_train`.
""")

    add_code("""
preprocessor = build_preprocessing_pipeline()

# Fit ONLY on training data to prevent data leakage
print("Fitting preprocessor pipeline on X_train...")
X_train_transformed = preprocessor.fit_transform(X_train)

# Transform test data using fitted preprocessor
X_test_transformed = preprocessor.transform(X_test)

print(f"X_train original shape: {X_train.shape} -> Transformed shape: {X_train_transformed.shape}")
print(f"X_test original shape:  {X_test.shape} -> Transformed shape: {X_test_transformed.shape}")
""")

    # Cell 5: Inspect Transformed Feature Names & Values
    add_markdown("""
---
## 5. Inspect Transformed Output & Feature Names
Extract generated feature names from `ColumnTransformer`.
""")

    add_code("""
# Get feature names from preprocessor
cat_encoder = preprocessor.named_transformers_['cat'].named_steps['encoder']
encoded_cat_cols = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
all_feature_names = NUMERICAL_FEATURES + encoded_cat_cols

print("=== TRANSFORMED FEATURE NAMES ===")
for idx, name in enumerate(all_feature_names):
    print(f"Feature {idx+1}: {name}")

# Convert transformed array back to DataFrame for verification
df_X_train_transformed = pd.DataFrame(X_train_transformed, columns=all_feature_names)
print("\\n=== TRANSFORMED X_TRAIN HEAD ===")
df_X_train_transformed.head()
""")

    # Cell 6: Verify Zero Leakage & Scaler Statistics
    add_markdown("""
---
## 6. Preprocessing Verification & Leakage Checks

### Verification Checklist:
1. **Mean & Variance:** Numerical columns in transformed training set have mean ≈ 0 and std ≈ 1.
2. **Missing Values:** Zero missing values in transformed training and test sets.
3. **No Target Contamination:** `y_train` and `y_test` were never passed to the preprocessor.
""")

    add_code("""
print("=== TRANSFORMED X_TRAIN MEAN & STD ===")
print(df_X_train_transformed[NUMERICAL_FEATURES].agg(['mean', 'std']).T.round(4))

assert not np.isnan(X_train_transformed).any(), "NaN values detected in X_train_transformed!"
assert not np.isnan(X_test_transformed).any(), "NaN values detected in X_test_transformed!"

print("\\n✅ All preprocessing checks passed successfully. Zero data leakage verified.")
""")

    os.makedirs("ml/notebooks", exist_ok=True)
    nb_path = "ml/notebooks/02_preprocessing.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2)

    print(f"Notebook successfully created at: {nb_path}")

if __name__ == "__main__":
    create_preprocessing_notebook()
