import logging
import requests
from django.conf import settings
from typing import Dict, Any

# Local ML module imports for failover fallback
from ml.src.predict import predict_stress
from ml.src.explain import explain_prediction

logger = logging.getLogger(__name__)

try:
    from django.conf import settings
    if settings.configured:
        FASTAPI_BASE_URL = getattr(settings, 'FASTAPI_SERVICE_URL', 'http://127.0.0.1:8001')
    else:
        FASTAPI_BASE_URL = 'http://127.0.0.1:8001'
except Exception:
    FASTAPI_BASE_URL = 'http://127.0.0.1:8001'

FASTAPI_ANALYZE_ENDPOINT = f"{FASTAPI_BASE_URL}/api/v1/analyze"


def get_assessment_analysis(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieves ML prediction and SHAP explanation for a student assessment.
    
    Tries HTTP API call to FastAPI microservice first.
    If FastAPI is unreachable or times out, seamlessly falls back to direct local Python ML execution.

    Parameters:
        input_dict (Dict[str, Any]): Dictionary of student lifestyle inputs.

    Returns:
        Dict[str, Any]: Unified analysis payload containing prediction and explanation attributes.
    """
    # 1. Attempt HTTP REST API call to FastAPI microservice
    try:
        payload = {
            'student_type': str(input_dict.get('Student_Type', 'college')),
            'sleep_hours': float(input_dict.get('Sleep_Hours', 7.0)),
            'study_hours': float(input_dict.get('Study_Hours', 5.0)),
            'social_media_hours': float(input_dict.get('Social_Media_Hours', 2.0)),
            'attendance': float(input_dict.get('Attendance', 85.0)),
            'exam_pressure': float(input_dict.get('Exam_Pressure', 5.0)),
            'family_support': float(input_dict.get('Family_Support', 7.0)),
            'month': float(input_dict.get('Month', 9.0)),
        }

        response = requests.post(FASTAPI_ANALYZE_ENDPOINT, json=payload, timeout=2.5)

        if response.status_code == 200:
            data = response.json()
            logger.info("Successfully received analysis from FastAPI microservice.")
            return {
                'prediction_code': data['prediction']['prediction_code'],
                'predicted_label': data['prediction']['predicted_label'],
                'probabilities': data['prediction']['probabilities'],
                'model_version': data['prediction']['model_version'],
                'top_contributing_factors': data['explanation']['top_contributing_factors'],
                'narrative_explanation': data['explanation']['narrative_explanation'],
                'source': 'fastapi'
            }
        else:
            logger.warning(f"FastAPI returned non-200 status code ({response.status_code}). Triggering fallback.")

    except requests.RequestException as e:
        logger.info(f"FastAPI microservice unreachable ({str(e)}). Using local Python ML engine fallback.")

    # 2. Fallback to direct local Python ML execution
    pred_result = predict_stress(input_dict)
    shap_result = explain_prediction(input_dict)

    return {
        'prediction_code': pred_result['prediction_code'],
        'predicted_label': pred_result['predicted_label'],
        'probabilities': pred_result['probabilities'],
        'model_version': pred_result['model_version'],
        'top_contributing_factors': shap_result['top_contributing_factors'],
        'narrative_explanation': shap_result['narrative_explanation'],
        'source': 'local_fallback'
    }

