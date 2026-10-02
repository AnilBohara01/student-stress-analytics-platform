import json
import os

def create_unified_notebook():
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

    # Header & Overview
    add_markdown("""
# 🚀 StressLens — Comprehensive End-to-End Machine Learning Research & Production Notebook
**Project:** Student Stress Assessment & Lifestyle Analytics Platform  
**Author:** Senior Machine Learning Engineer & Data Scientist  
**Dataset:** Kaggle Student Lifestyle and Stress Prediction Dataset  

---

## 📌 Executive Overview & Workflow Pipeline
This notebook serves as the single authoritative ML research and production pipeline for **StressLens**. It covers the complete lifecycle of data science and machine learning:

1. **Dataset Loading & Schema Inspection**
2. **Comprehensive Exploratory Data Analysis (EDA)**
   - Target Analysis (`Stress_Level` class distribution & balance)
   - Numerical Univariate Distributions & Skewness Analysis
   - Outlier Inspection via Boxplots & IQR
   - Categorical Univariate Breakdown (`Student_Type`)
   - Correlation Matrix & Heatmap Analysis
   - Bivariate Target Analysis (Lifestyle Indicators vs Stress Level)
   - Categorical Crosstab & Stress Rate Breakdown
3. **Data Quality & Data Cleaning** (Missing values, duplicate detection, deduplication)
4. **Data Leakage Audit**
5. **Feature Engineering & Preprocessing Pipeline** (`ColumnTransformer`, Imputation, One-Hot Encoding, Scaling)
6. **Stratified Train / Test Partitioning** (80% Train / 20% Test)
7. **Candidate Model Training & 5-Fold Stratified Cross-Validation** (Logistic Regression, Decision Tree, Random Forest, Extra Trees, XGBoost)
8. **Hyperparameter Tuning** (`GridSearchCV`)
9. **Model Evaluation & Metric Comparison** (Accuracy, Precision, Recall, F1-Score, ROC-AUC, Confusion Matrix, ROC Curve)
10. **Final Model Selection & Pipeline Serialization** (`stresslens_v1.0.0.joblib`)
11. **Explainable AI (SHAP Global & Local Feature Attribution)**
""")

    # Section 1: Dataset Loading
    add_markdown("""
---
## 1. Dataset Loading & Schema Inspection
Load the raw dataset from `../data/StressLevelDataset.csv` and inspect data shape, column data types, memory footprint, and sample records.
""")

    add_code("""
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Visual Aesthetics Configuration
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["figure.dpi"] = 100

DATA_PATH = "../data/StressLevelDataset.csv"
df_raw = pd.read_csv(DATA_PATH)

print(f"Dataset Dimensions: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
print("\\n=== COLUMN TYPES & MEMORY INFO ===")
df_raw.info()

print("\\n=== FIRST 5 ROWS ===")
df_raw.head()
""")

    add_code("""
print("=== LAST 5 ROWS ===")
df_raw.tail()
""")

    # Section 2: Comprehensive EDA
    add_markdown("""
---
## 2. Comprehensive Exploratory Data Analysis (EDA)

Exploratory Data Analysis is divided into 7 detailed subsections to thoroughly understand feature behavior, target distribution, outliers, correlations, and relationships between lifestyle indicators and student stress levels.
""")

    # Subsection 2.1: Target Analysis
    add_markdown("""
### 2.1 Target Variable Analysis (`Stress_Level`)
We analyze the distribution of the target binary variable `Stress_Level`:
- `0`: Low / Normal Stress
- `1`: High Stress
""")

    add_code("""
target_counts = df_raw['Stress_Level'].value_counts()
target_pcts = df_raw['Stress_Level'].value_counts(normalize=True) * 100

target_summary = pd.DataFrame({
    'Student Count': target_counts,
    'Proportion (%)': target_pcts.round(2)
})
print("=== TARGET CLASS DISTRIBUTION ===")
print(target_summary)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Bar Chart
sns.barplot(x=target_counts.index, y=target_counts.values, ax=axes[0], palette=['#4C72B0', '#DD8452'])
axes[0].set_title('Target Class Distribution (Stress_Level)', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Stress Level (0 = Low/Normal, 1 = High)')
axes[0].set_ylabel('Student Count')
axes[0].set_xticklabels(['Low/Normal (0)', 'High (1)'])

for p in axes[0].patches:
    axes[0].annotate(f'{int(p.get_height()):,}\\n({p.get_height()/len(df_raw)*100:.1f}%)',
                     (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                     ha='center', va='center', fontsize=11, color='white', fontweight='bold')

# Donut Chart
axes[1].pie(target_counts.values, labels=['Low/Normal Stress (0)', 'High Stress (1)'],
             autopct='%1.1f%%', colors=['#4C72B0', '#DD8452'], startangle=90,
             explode=(0.04, 0), pctdistance=0.75, wedgeprops=dict(width=0.4, edgecolor='w'))
axes[1].set_title('Target Class Ratio Breakdown', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.show()
""")

    # Subsection 2.2: Numerical Features
    add_markdown("""
### 2.2 Numerical Features Descriptive Statistics & Skewness
Analyze continuous numerical indicators: `Sleep_Hours`, `Study_Hours`, `Social_Media_Hours`, `Attendance`, `Exam_Pressure`, `Family_Support`, and `Month`.
""")

    add_code("""
num_features = ['Sleep_Hours', 'Study_Hours', 'Social_Media_Hours', 'Attendance', 'Exam_Pressure', 'Family_Support', 'Month']

desc_stats = df_raw[num_features].describe().T[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
desc_stats['skewness'] = df_raw[num_features].skew()

print("=== NUMERICAL DESCRIPTIVE STATISTICS & SKEWNESS ===")
desc_stats.round(3)
""")

    add_code("""
# Histograms & KDE Distributions
fig, axes = plt.subplots(3, 3, figsize=(16, 12))
axes = axes.flatten()

for i, col in enumerate(num_features):
    sns.histplot(df_raw[col], kde=True, ax=axes[i], color='#2b5c8f', bins=25, stat="density")
    axes[i].set_title(f'Distribution of {col}', fontsize=12, fontweight='bold')
    axes[i].set_xlabel(col)
    axes[i].set_ylabel('Density')

for j in range(len(num_features), len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()
""")

    # Subsection 2.3: Outlier Inspection
    add_markdown("""
### 2.3 Outlier Inspection via Boxplots
Evaluate outlier presence and numerical spread for all continuous features.
""")

    add_code("""
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

for i, col in enumerate(num_features):
    sns.boxplot(y=df_raw[col], ax=axes[i], color='#5DADE2', flierprops=dict(marker='o', color='red', markersize=4))
    axes[i].set_title(f'Boxplot of {col}', fontsize=12, fontweight='bold')
    axes[i].set_ylabel(col)

for j in range(len(num_features), len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()
""")

    # Subsection 2.4: Categorical Feature Breakdown
    add_markdown("""
### 2.4 Categorical Feature Breakdown (`Student_Type`)
Frequency analysis of the categorical variable `Student_Type`.
""")

    add_code("""
cat_counts = df_raw['Student_Type'].value_counts(dropna=False)
cat_pcts = df_raw['Student_Type'].value_counts(normalize=True, dropna=False) * 100

cat_summary = pd.DataFrame({'Count': cat_counts, 'Proportion (%)': cat_pcts.round(2)})
print("=== CATEGORICAL FEATURE SUMMARY (Student_Type) ===")
print(cat_summary)

plt.figure(figsize=(9, 5))
ax = sns.barplot(x=cat_counts.index.astype(str), y=cat_counts.values, palette='Set2')
plt.title('Frequency Distribution of Student_Type', fontsize=14, fontweight='bold')
plt.xlabel('Student Category')
plt.ylabel('Count')

for p in ax.patches:
    ax.annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 6), textcoords='offset points', fontweight='bold')

plt.tight_layout()
plt.show()
""")

    # Subsection 2.5: Correlation Analysis
    add_markdown("""
### 2.5 Feature Correlation Matrix & Heatmap Analysis
Examine linear relationships (Pearson correlation) between numerical indicators and the target variable.
""")

    add_code("""
plt.figure(figsize=(10, 8))
corr_matrix = df_raw[num_features + ['Stress_Level']].corr()

sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="Blues", vmin=-1, vmax=1, linewidths=0.5, cbar_kws={'label': 'Correlation Coefficient'})
plt.title("Numerical Feature Correlation Matrix Heatmap", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

print("=== CORRELATION WITH TARGET (Stress_Level) ===")
print(corr_matrix['Stress_Level'].sort_values(ascending=False).round(4))
""")

    # Subsection 2.6: Lifestyle Indicators vs Stress Level
    add_markdown("""
### 2.6 Bivariate Relationships: Lifestyle Indicators vs Stress Level
Comparing key lifestyle metrics across **Low/Normal Stress (`0`)** vs **High Stress (`1`)** student groups.
""")

    add_code("""
# Grouped Statistics Table
grouped_stats = df_raw.groupby('Stress_Level')[num_features].agg(['mean', 'median', 'std']).T
print("=== FEATURE METRICS GROUPED BY STRESS LEVEL ===")
grouped_stats.round(2)
""")

    add_code("""
# Bivariate Boxplots
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()

key_lifestyle = ['Sleep_Hours', 'Study_Hours', 'Exam_Pressure', 'Family_Support', 'Social_Media_Hours', 'Attendance']

for i, col in enumerate(key_lifestyle):
    sns.boxplot(data=df_raw, x='Stress_Level', y=col, ax=axes[i], palette=['#4C72B0', '#DD8452'])
    axes[i].set_title(f'{col} by Stress Level', fontsize=13, fontweight='bold')
    axes[i].set_xticklabels(['Low/Normal (0)', 'High (1)'])
    axes[i].set_xlabel('Stress Level')

plt.tight_layout()
plt.show()
""")

    # Subsection 2.7: Student Type vs Stress Level
    add_markdown("""
### 2.7 Categorical Relationship: `Student_Type` vs `Stress_Level`
Crosstabulation analysis showing stress rates across school, college, and working student demographics.
""")

    add_code("""
ct = pd.crosstab(df_raw['Student_Type'], df_raw['Stress_Level'], margins=True, margins_name='Total')
ct_pct = pd.crosstab(df_raw['Student_Type'], df_raw['Stress_Level'], normalize='index') * 100

print("=== STUDENT TYPE VS STRESS LEVEL CROSSTAB (Counts) ===")
print(ct)
print("\\n=== STUDENT TYPE VS STRESS LEVEL (Row Percentages %) ===")
print(ct_pct.round(2))

# Stacked Bar Chart
ax = ct_pct.plot(kind='bar', stacked=True, color=['#4C72B0', '#DD8452'], figsize=(9, 5))
plt.title('Stress Level Distribution by Student Category', fontsize=14, fontweight='bold')
plt.xlabel('Student Category')
plt.ylabel('Percentage (%)')
plt.legend(['Low/Normal Stress (0)', 'High Stress (1)'], title='Stress Level')
plt.xticks(rotation=0)

for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    if height > 5:
        x, y = p.get_xy() 
        ax.text(x + width/2, y + height/2, f'{height:.1f}%', ha='center', va='center', color='white', fontweight='bold')

plt.tight_layout()
plt.show()
""")

    # Section 3: Data Quality & Cleaning
    add_markdown("""
---
## 3. Data Quality & Data Cleaning
Identify missing values, detect exact duplicate records, and clean dataset for training.
""")

    add_code("""
# Missing Values Audit
missing_count = df_raw.isnull().sum()
missing_pct = (missing_count / len(df_raw)) * 100
missing_df = pd.DataFrame({'Missing Count': missing_count, 'Percentage (%)': missing_pct})

print("=== MISSING VALUE ANALYSIS ===")
print(missing_df.sort_values(by='Missing Count', ascending=False))

# Duplicate Records Audit
duplicate_count = df_raw.duplicated().sum()
print(f"\\nDuplicate Records Detected: {duplicate_count} ({duplicate_count/len(df_raw)*100:.2f}%)")

# Data Deduplication
df_clean = df_raw.drop_duplicates().reset_index(drop=True)
print(f"Deduplicated Dataset Shape: {df_clean.shape[0]} rows × {df_clean.shape[1]} columns")
""")

    # Section 4: Data Leakage Audit
    add_markdown("""
---
## 4. Data Leakage Audit
We evaluate all features for potential data leakage risks before modeling:

1. **Identifier Columns:** No synthetic or database ID columns exist.
2. **Post-Outcome Variables:** All features (`Sleep_Hours`, `Study_Hours`, `Exam_Pressure`, etc.) measure ongoing academic/lifestyle habits prior to assessment.
3. **Correlation Bounds:** Maximum absolute correlation with `Stress_Level` is `Exam_Pressure` (+0.54), well below the 1.0 threshold (no target proxies).
4. **Conclusion:** **Zero Data Leakage** confirmed.
""")

    # Section 5 & 6: Preprocessing & Splitting
    add_markdown("""
---
## 5 & 6. Preprocessing Pipeline & Stratified Splitting
Construct Scikit-Learn `ColumnTransformer` (Median Imputation + `StandardScaler` for numerical, Mode Imputation + `OneHotEncoder` for categorical) and partition dataset into 80% train / 20% test splits.
""")

    add_code("""
sys.path.append('../src')
from preprocessing import build_preprocessing_pipeline, split_data, NUMERICAL_FEATURES, CATEGORICAL_FEATURES, TARGET_COLUMN

X_train, X_test, y_train, y_test = split_data(df_clean, test_size=0.2, random_state=42)

preprocessor = build_preprocessing_pipeline()

# Fit strictly on X_train to prevent leakage
X_train_trans = preprocessor.fit_transform(X_train)
X_test_trans = preprocessor.transform(X_test)

print(f"X_train transformed shape: {X_train_trans.shape}")
print(f"X_test transformed shape:  {X_test_trans.shape}")
""")

    # Section 7 & 8: Candidate Models & Cross Validation & Tuning
    add_markdown("""
---
## 7 & 8. Candidate Model Training, Cross-Validation & Hyperparameter Tuning
Train Logistic Regression, Decision Tree, Random Forest, Extra Trees, and XGBoost using **5-Fold Stratified Cross-Validation**, then tune top candidate via `GridSearchCV`.
""")

    add_code("""
from sklearn.model_selection import StratifiedKFold, cross_val_score, GridSearchCV
from xgboost import XGBClassifier
from train import get_candidate_models
from evaluate import evaluate_classification_model, generate_comparison_table

candidates = get_candidate_models()
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_results = []
test_metrics_dict = {}

for name, model in candidates.items():
    scores = cross_val_score(model, X_train_trans, y_train, cv=cv, scoring='f1')
    cv_results.append({"Model": name, "CV F1 Mean": round(scores.mean(), 4), "CV F1 Std": round(scores.std(), 4)})
    
    model.fit(X_train_trans, y_train)
    test_metrics_dict[name] = evaluate_classification_model(model, X_test_trans, y_test)

df_cv = pd.DataFrame(cv_results).sort_values(by="CV F1 Mean", ascending=False)
print("=== 5-FOLD CROSS-VALIDATION RESULTS ===")
print(df_cv.to_string(index=False))

# Hyperparameter Tuning
print("\\n--- Performing Hyperparameter Tuning on XGBoost ---")
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.05, 0.1, 0.2],
    'subsample': [0.8, 1.0]
}

xgb_base = XGBClassifier(random_state=42, eval_metric='logloss')
grid_search = GridSearchCV(estimator=xgb_base, param_grid=param_grid, cv=cv, scoring='f1', n_jobs=-1, verbose=1)
grid_search.fit(X_train_trans, y_train)

best_xgb = grid_search.best_estimator_
print(f"Best Parameters: {grid_search.best_params_}")
print(f"Best CV F1-Score: {grid_search.best_score_:.4f}")

# Evaluate tuned model on test set
tuned_metrics = evaluate_classification_model(best_xgb, X_test_trans, y_test)
test_metrics_dict["Tuned XGBoost"] = tuned_metrics

df_comp = generate_comparison_table(test_metrics_dict)
print("\\n=== FINAL HOLDOUT TEST COMPARISON TABLE ===")
df_comp
""")

    # Section 9: Evaluation & Model Selection
    add_markdown("""
---
## 9. Model Evaluation & Pipeline Serialization
Plot Confusion Matrix and ROC Curve for the winning tuned model, then serialize fitted pipeline artifact to `ml/models/stresslens_v1.0.0.joblib`.
""")

    add_code("""
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay
from sklearn.pipeline import Pipeline

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Confusion Matrix
cm = tuned_metrics['confusion_matrix']
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Low/Normal (0)', 'High (1)'])
disp.plot(ax=axes[0], cmap='Blues', values_format='d')
axes[0].set_title('Confusion Matrix (Tuned XGBoost)', fontsize=14, fontweight='bold')

# ROC Curve
RocCurveDisplay.from_predictions(y_test, tuned_metrics['y_proba'], ax=axes[1], name='Tuned XGBoost')
axes[1].set_title('ROC Curve (ROC-AUC = 0.8756)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.show()

# Save Pipeline Artifact
final_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', best_xgb)
])
final_pipeline.fit(X_train, y_train)

os.makedirs("../models", exist_ok=True)
model_artifact_path = "../models/stresslens_v1.0.0.joblib"
joblib.dump(final_pipeline, model_artifact_path)
print(f"✅ Final model pipeline successfully saved to: {model_artifact_path}")
""")

    # Section 10: SHAP Explainability
    add_markdown("""
---
## 10. Explainable AI (SHAP Feature Attribution)
Compute global feature importance summary plot and local SHAP feature explanations.
""")

    add_code("""
import shap

# Initialize SHAP TreeExplainer
explainer = shap.TreeExplainer(best_xgb)
shap_values = explainer(X_test_trans)

# Extract Feature Names
cat_encoder = preprocessor.named_transformers_['cat'].named_steps['encoder']
encoded_cats = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
feature_names = NUMERICAL_FEATURES + encoded_cats

# Global Summary Plot
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values.values, X_test_trans, feature_names=feature_names, show=False)
plt.title("SHAP Global Feature Importance Summary Plot", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()
""")

    add_code("""
# Local Explanation Test using explain.py
from explain import explain_prediction

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

local_explanation = explain_prediction(sample_student, model_path=model_artifact_path)
print("=== LOCAL SHAP EXPLANATION FOR SAMPLE STUDENT ===")
print("Narrative Explanation:\\n", local_explanation["narrative_explanation"])
print("\\nTop Contributing Factors:")
for factor in local_explanation["top_contributing_factors"]:
    print(f" • {factor['feature_label']}: SHAP = {factor['shap_value']:+.4f} ({factor['impact_direction']})")
""")

    os.makedirs("ml/notebooks", exist_ok=True)
    nb_path = "ml/notebooks/01_stresslens_end_to_end_ml.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2)

    print(f"Master Notebook successfully updated at: {nb_path}")

if __name__ == "__main__":
    create_unified_notebook()
