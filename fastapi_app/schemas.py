from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class StudentAssessmentRequest(BaseModel):
    student_type: str = Field(
        default="college",
        description="Category of student: 'college', 'school', or 'working_student'",
        examples=["college"]
    )
    sleep_hours: float = Field(
        default=7.0,
        ge=0.0,
        le=24.0,
        description="Average daily sleep duration in hours (0 to 24)",
        examples=[6.5]
    )
    study_hours: float = Field(
        default=5.0,
        ge=0.0,
        le=24.0,
        description="Average daily study duration in hours (0 to 24)",
        examples=[7.0]
    )
    social_media_hours: float = Field(
        default=2.0,
        ge=0.0,
        le=24.0,
        description="Average daily social media usage in hours (0 to 24)",
        examples=[3.5]
    )
    attendance: float = Field(
        default=85.0,
        ge=0.0,
        le=100.0,
        description="Academic class attendance percentage (0 to 100)",
        examples=[80.0]
    )
    exam_pressure: float = Field(
        default=5.0,
        ge=0.0,
        le=10.0,
        description="Perceived exam pressure rating (0 to 10)",
        examples=[8.0]
    )
    family_support: float = Field(
        default=7.0,
        ge=0.0,
        le=10.0,
        description="Perceived family support rating (0 to 10)",
        examples=[5.0]
    )
    month: float = Field(
        default=9.0,
        ge=1.0,
        le=12.0,
        description="Academic month index (1 to 12)",
        examples=[10.0]
    )

class PredictionProbabilities(BaseModel):
    low_normal_stress: float = Field(description="Probability of Low/Normal Stress (Class 0)")
    high_stress: float = Field(description="Probability of High Stress (Class 1)")

class StressPredictionResponse(BaseModel):
    prediction_code: int = Field(description="0 for Low/Normal Stress, 1 for High Stress")
    predicted_label: str = Field(description="Human-readable stress class label")
    probabilities: PredictionProbabilities
    model_version: str = Field(description="Model artifact version")

class SHAPFactorImpact(BaseModel):
    feature_raw: str = Field(description="Internal raw feature variable name")
    feature_label: str = Field(description="Human-readable feature description")
    shap_value: float = Field(description="Calculated SHAP attribution score")
    impact_direction: str = Field(description="'increases_stress' or 'decreases_stress'")
    abs_impact: float = Field(description="Absolute magnitude of SHAP attribution")

class SHAPExplanationResponse(BaseModel):
    top_contributing_factors: List[SHAPFactorImpact] = Field(description="Top key lifestyle factors influencing stress score")
    narrative_explanation: str = Field(description="Non-clinical AI summary text explaining stress drivers")

class CombinedAnalysisResponse(BaseModel):
    prediction: StressPredictionResponse
    explanation: SHAPExplanationResponse
    status: str = Field(default="success", description="Response status indicator")

class HealthCheckResponse(BaseModel):
    status: str = Field(description="Server health status ('ok')")
    service: str = Field(description="Service name")
    model_version: str = Field(description="Active ML model pipeline version")
    model_loaded: bool = Field(description="Boolean flag indicating if ML model pipeline is loaded in memory")
