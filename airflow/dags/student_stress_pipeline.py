import os
import sys
from datetime import datetime, timedelta

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    HAS_AIRFLOW = True
except ImportError:
    HAS_AIRFLOW = False
    DAG = None
    PythonOperator = None



# Add ml/src to Python path for pipeline execution inside Airflow workers
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, 'ml', 'src'))


def validate_raw_data_task():
    """
    Task 1: Validates raw dataset existence and verifies column schema.
    """
    data_path = os.path.join(PROJECT_ROOT, 'ml', 'data', 'StressLevelDataset.csv')
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Raw dataset file missing at: {data_path}")

    import pandas as pd
    df = pd.read_csv(data_path)
    expected_cols = [
        'Student_Type', 'Sleep_Hours', 'Study_Hours', 'Social_Media_Hours',
        'Attendance', 'Exam_Pressure', 'Family_Support', 'Month', 'Stress_Level'
    ]

    for col in expected_cols:
        if col not in df.columns:
            raise KeyError(f"Expected column '{col}' missing from raw dataset.")

    print(f"Data Validation Passed: {len(df)} rows, all expected columns present.")


def preprocess_dataset_task():
    """
    Task 2: Executes dataset deduplication and preprocessing pipeline setup.
    """
    from preprocessing import load_and_clean_data, build_preprocessing_pipeline, split_data
    
    data_path = os.path.join(PROJECT_ROOT, 'ml', 'data', 'StressLevelDataset.csv')
    df_clean = load_and_clean_data(data_path)
    X_tr, X_te, y_tr, y_te = split_data(df_clean)

    preprocessor = build_preprocessing_pipeline()
    X_tr_trans = preprocessor.fit_transform(X_tr)

    print(f"Preprocessing Task Complete: X_train shape = {X_tr_trans.shape}")


def train_and_evaluate_model_task():
    """
    Task 3: Executes candidate model cross-validation, hyperparameter tuning, and pipeline serialization.
    """
    from train import train_and_evaluate_all
    pipeline, comp_df, tuned_metrics = train_and_evaluate_all()
    print("Training Task Complete: Model Pipeline serialized and ready for inference.")


def verify_shap_explanations_task():
    """
    Task 4: Verifies SHAP explainer output for a sample student record.
    """
    from explain import explain_prediction

    sample_student = {
        "Student_Type": "college",
        "Sleep_Hours": 6.0,
        "Study_Hours": 7.5,
        "Social_Media_Hours": 3.0,
        "Attendance": 80.0,
        "Exam_Pressure": 7.5,
        "Family_Support": 5.0,
        "Month": 9.0
    }

    explanation = explain_prediction(sample_student)
    print("SHAP Verification Passed:", explanation['narrative_explanation'])


if HAS_AIRFLOW:
    default_args = {
        'owner': 'stresslens_mlops',
        'depends_on_past': False,
        'start_date': datetime(2026, 1, 1),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }

    with DAG(
        dag_id='student_stress_ml_pipeline',
        default_args=default_args,
        description='Automated ML Pipeline for Student Stress Assessment Platform',
        schedule_interval='@monthly',
        catchup=False,
        tags=['machine_learning', 'stresslens', 'xgboost', 'shap']
    ) as dag:

        t1_validate = PythonOperator(
            task_id='validate_raw_data',
            python_callable=validate_raw_data_task
        )

        t2_preprocess = PythonOperator(
            task_id='preprocess_dataset',
            python_callable=preprocess_dataset_task
        )

        t3_train = PythonOperator(
            task_id='train_and_evaluate_model',
            python_callable=train_and_evaluate_model_task
        )

        t4_explain = PythonOperator(
            task_id='verify_shap_explanations',
            python_callable=verify_shap_explanations_task
        )

        # Task Dependencies Workflow
        t1_validate >> t2_preprocess >> t3_train >> t4_explain

