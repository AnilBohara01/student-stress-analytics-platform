import sys
import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root and ml/src to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

ML_SRC_DIR = os.path.join(BASE_DIR, 'ml', 'src')
if ML_SRC_DIR not in sys.path:
    sys.path.append(ML_SRC_DIR)

from ml.src.predict import predict_stress, load_model_pipeline, MODEL_VERSION
from ml.src.explain import explain_prediction
from fastapi_app.schemas import (
    StudentAssessmentRequest,
    StressPredictionResponse,
    SHAPExplanationResponse,
    CombinedAnalysisResponse,
    HealthCheckResponse,
    PredictionProbabilities
)

app = FastAPI(
    title="Student Stress Assessment & Lifestyle Analytics API",
    description="High-performance FastAPI microservice delivering machine learning stress prediction (XGBoost) and Explainable AI (SHAP) feature attributions for higher education students.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _convert_schema_to_ml_dict(request_data: StudentAssessmentRequest) -> dict:
    """Helper function to map Pydantic request to ML module feature dictionary keys."""
    return {
        'Student_Type': request_data.student_type,
        'Sleep_Hours': request_data.sleep_hours,
        'Study_Hours': request_data.study_hours,
        'Social_Media_Hours': request_data.social_media_hours,
        'Attendance': request_data.attendance,
        'Exam_Pressure': request_data.exam_pressure,
        'Family_Support': request_data.family_support,
        'Month': request_data.month,
    }

@app.on_event("startup")
def startup_event():
    """Pre-load ML model pipeline into memory during FastAPI startup."""
    try:
        load_model_pipeline()
        print("✅ FastAPI ML Microservice initialized successfully.")
    except Exception as e:
        print(f"⚠️ Warning: Could not pre-load ML model pipeline on startup: {str(e)}")

@app.get("/", tags=["Metadata"])
def root_info():
    """Welcome endpoint providing service status and API links."""
    return {
        "service": "Student Stress Assessment FastAPI Microservice",
        "status": "online",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "predict": "/api/v1/predict",
            "explain": "/api/v1/explain",
            "analyze": "/api/v1/analyze"
        }
    }

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
def health_check():
    """Health check endpoint verifying model readiness."""
    try:
        pipeline = load_model_pipeline()
        model_loaded = pipeline is not None
    except Exception:
        model_loaded = False

    return HealthCheckResponse(
        status="ok" if model_loaded else "degraded",
        service="FastAPI Stress Analytics Engine",
        model_version=MODEL_VERSION,
        model_loaded=model_loaded
    )

@app.post("/api/v1/predict", response_model=StressPredictionResponse, tags=["Machine Learning"])
def predict_endpoint(payload: StudentAssessmentRequest):
    """
    Generates a stress risk prediction (Low/Normal Stress vs. High Stress) and class probabilities for student lifestyle input.
    """
    try:
        input_dict = _convert_schema_to_ml_dict(payload)
        pred_result = predict_stress(input_dict)

        return StressPredictionResponse(
            prediction_code=pred_result["prediction_code"],
            predicted_label=pred_result["predicted_label"],
            probabilities=PredictionProbabilities(
                low_normal_stress=pred_result["probabilities"]["low_normal_stress"],
                high_stress=pred_result["probabilities"]["high_stress"]
            ),
            model_version=pred_result["model_version"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction service error: {str(e)}"
        )

@app.post("/api/v1/explain", response_model=SHAPExplanationResponse, tags=["Explainable AI (SHAP)"])
def explain_endpoint(payload: StudentAssessmentRequest):
    """
    Computes SHAP feature attributions and returns top risk drivers and narrative explanation.
    """
    try:
        input_dict = _convert_schema_to_ml_dict(payload)
        shap_result = explain_prediction(input_dict)

        return SHAPExplanationResponse(
            top_contributing_factors=shap_result["top_contributing_factors"],
            narrative_explanation=shap_result["narrative_explanation"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SHAP explanation service error: {str(e)}"
        )

@app.post("/api/v1/analyze", response_model=CombinedAnalysisResponse, tags=["Full Analytics"])
def analyze_endpoint(payload: StudentAssessmentRequest):
    """
    Unified endpoint performing prediction and SHAP explainability analysis in a single HTTP request.
    """
    try:
        input_dict = _convert_schema_to_ml_dict(payload)
        pred_result = predict_stress(input_dict)
        shap_result = explain_prediction(input_dict)

        prediction_response = StressPredictionResponse(
            prediction_code=pred_result["prediction_code"],
            predicted_label=pred_result["predicted_label"],
            probabilities=PredictionProbabilities(
                low_normal_stress=pred_result["probabilities"]["low_normal_stress"],
                high_stress=pred_result["probabilities"]["high_stress"]
            ),
            model_version=pred_result["model_version"]
        )

        explanation_response = SHAPExplanationResponse(
            top_contributing_factors=shap_result["top_contributing_factors"],
            narrative_explanation=shap_result["narrative_explanation"]
        )

        return CombinedAnalysisResponse(
            prediction=prediction_response,
            explanation=explanation_response,
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline error: {str(e)}"
        )
