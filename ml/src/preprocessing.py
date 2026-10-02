import os
from typing import Tuple, List
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

NUMERICAL_FEATURES: List[str] = [
    'Sleep_Hours',
    'Study_Hours',
    'Social_Media_Hours',
    'Attendance',
    'Exam_Pressure',
    'Family_Support',
    'Month'
]

CATEGORICAL_FEATURES: List[str] = ['Student_Type']
TARGET_COLUMN: str = 'Stress_Level'


def load_and_clean_data(data_path: str = 'ml/data/StressLevelDataset.csv') -> pd.DataFrame:
    """
    Loads raw CSV dataset and removes duplicate rows.

    Parameters:
        data_path (str): Path to the CSV dataset file.

    Returns:
        pd.DataFrame: Cleaned pandas DataFrame.
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset file not found at: {data_path}")

    df = pd.read_csv(data_path)
    initial_count = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    deduped_count = len(df)
    print(f"Data Loaded: {initial_count} initial rows -> {deduped_count} rows after removing duplicates.")
    return df


def build_preprocessing_pipeline() -> ColumnTransformer:
    """
    Constructs a Scikit-Learn ColumnTransformer containing numerical and categorical processing pipelines.

    Returns:
        ColumnTransformer: Preprocessing pipeline transformer.
    """
    num_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    cat_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, NUMERICAL_FEATURES),
            ('cat', cat_pipeline, CATEGORICAL_FEATURES)
        ],
        remainder='drop'
    )
    return preprocessor


def split_data(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Splits feature matrix X and target vector y into stratified training and testing sets.

    Parameters:
        df (pd.DataFrame): Input dataset containing features and target.
        test_size (float): Proportion of the dataset to include in the test split.
        random_state (int): Seed for random number generation.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]: X_train, X_test, y_train, y_test
    """
    if TARGET_COLUMN not in df.columns:
        raise KeyError(f"Target column '{TARGET_COLUMN}' not found in dataset columns.")

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

    print(f"Data Split Complete: Train={len(X_train)} samples, Test={len(X_test)} samples (Stratified on '{TARGET_COLUMN}')")
    return X_train, X_test, y_train, y_test


if __name__ == '__main__':
    # Standalone execution test
    df_clean = load_and_clean_data()
    pipeline = build_preprocessing_pipeline()
    X_tr, X_te, y_tr, y_te = split_data(df_clean)

    # Fit pipeline strictly on training data
    X_tr_transformed = pipeline.fit_transform(X_tr)
    X_te_transformed = pipeline.transform(X_te)

    print(f"Transformed X_train shape: {X_tr_transformed.shape}")
    print(f"Transformed X_test shape: {X_te_transformed.shape}")
    print("Preprocessing module test passed successfully!")
