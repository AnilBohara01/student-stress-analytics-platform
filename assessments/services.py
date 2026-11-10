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


def _get_rule_based_analysis(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Last-resort lightweight analysis when both FastAPI and local model artifacts are unavailable.
    """
    sleep_hours = float(input_dict.get('Sleep_Hours', 7.0))
    study_hours = float(input_dict.get('Study_Hours', 5.0))
    social_media_hours = float(input_dict.get('Social_Media_Hours', 2.0))
    attendance = float(input_dict.get('Attendance', 85.0))
    exam_pressure = float(input_dict.get('Exam_Pressure', 5.0))
    family_support = float(input_dict.get('Family_Support', 7.0))

    contribution_specs = [
        ('Sleep Hours', max(0.0, (7.0 - sleep_hours) / 7.0) * 0.22),
        ('Study Hours', min(1.0, study_hours / 10.0) * 0.12),
        ('Social Media Hours', min(1.0, social_media_hours / 8.0) * 0.18),
        ('Attendance', max(0.0, (85.0 - attendance) / 85.0) * 0.20),
        ('Exam Pressure', min(1.0, exam_pressure / 10.0) * 0.22),
        ('Family Support', max(0.0, (10.0 - family_support) / 10.0) * 0.16),
    ]
    stress_score = min(1.0, max(0.0, sum(score for _, score in contribution_specs)))
    prediction_code = 1 if stress_score >= 0.5 else 0
    predicted_label = "High Stress" if prediction_code == 1 else "Low/Normal Stress"

    top_contributing_factors = [
        {
            "feature_label": factor,
            "impact_direction": "increases_stress",
            "abs_impact": round(score, 4),
            "shap_value": round(score, 4),
        }
        for factor, score in sorted(contribution_specs, key=lambda item: item[1], reverse=True)[:3]
    ]

    return {
        'prediction_code': prediction_code,
        'predicted_label': predicted_label,
        'probabilities': {
            'low_normal_stress': round(1.0 - stress_score, 4),
            'high_stress': round(stress_score, 4),
        },
        'model_version': 'stresslens_v1.0.0',
        'top_contributing_factors': top_contributing_factors,
        'narrative_explanation': 'Model files were unavailable, so StressLens generated a conservative risk estimate using core lifestyle indicators.',
        'source': 'rule_based_fallback',
    }


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
    try:
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
    except Exception as e:
        logger.warning(f"Local ML fallback failed ({str(e)}). Using rule-based fallback.")
        return _get_rule_based_analysis(input_dict)
