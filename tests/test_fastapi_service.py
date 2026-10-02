import unittest
from fastapi.testclient import TestClient
from fastapi_app.main import app
from assessments.services import get_assessment_analysis

client = TestClient(app)

class FastAPIMicroserviceTestCase(unittest.TestCase):

    def test_root_endpoint(self):
        """Test GET / metadata endpoint."""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("predict", data["endpoints"])

    def test_health_check_endpoint(self):
        """Test GET /health endpoint."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["model_loaded"])

    def test_predict_endpoint_high_stress(self):
        """Test POST /api/v1/predict with high stress profile."""
        payload = {
            "student_type": "college",
            "sleep_hours": 3.0,
            "study_hours": 9.0,
            "social_media_hours": 5.0,
            "attendance": 65.0,
            "exam_pressure": 9.0,
            "family_support": 2.0,
            "month": 11.0
        }
        response = client.post("/api/v1/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("prediction_code", data)
        self.assertIn("predicted_label", data)
        self.assertIn("probabilities", data)
        self.assertIn("low_normal_stress", data["probabilities"])
        self.assertIn("high_stress", data["probabilities"])

    def test_explain_endpoint(self):
        """Test POST /api/v1/explain SHAP attributions."""
        payload = {
            "student_type": "college",
            "sleep_hours": 7.0,
            "study_hours": 5.0,
            "social_media_hours": 2.0,
            "attendance": 85.0,
            "exam_pressure": 5.0,
            "family_support": 7.0,
            "month": 9.0
        }
        response = client.post("/api/v1/explain", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("top_contributing_factors", data)
        self.assertIn("narrative_explanation", data)
        self.assertIsInstance(data["top_contributing_factors"], list)

    def test_analyze_combined_endpoint(self):
        """Test POST /api/v1/analyze unified endpoint."""
        payload = {
            "student_type": "college",
            "sleep_hours": 8.0,
            "study_hours": 4.0,
            "social_media_hours": 1.5,
            "attendance": 90.0,
            "exam_pressure": 3.0,
            "family_support": 8.0,
            "month": 5.0
        }
        response = client.post("/api/v1/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("prediction", data)
        self.assertIn("explanation", data)

    def test_invalid_input_validation(self):
        """Test Pydantic validation error handling for invalid input ranges."""
        payload = {
            "student_type": "college",
            "sleep_hours": 99.0, # Invalid sleep hours (> 24)
            "study_hours": 5.0,
            "social_media_hours": 2.0,
            "attendance": 85.0,
            "exam_pressure": 5.0,
            "family_support": 7.0,
            "month": 9.0
        }
        response = client.post("/api/v1/predict", json=payload)
        self.assertEqual(response.status_code, 422) # Unprocessable Entity

    def test_django_failover_service(self):
        """Test Django service fallback mechanism when FastAPI server is offline."""
        input_dict = {
            'Student_Type': 'college',
            'Sleep_Hours': 7.0,
            'Study_Hours': 5.0,
            'Social_Media_Hours': 2.0,
            'Attendance': 85.0,
            'Exam_Pressure': 5.0,
            'Family_Support': 7.0,
            'Month': 9.0,
        }
        # Calling service without running FastAPI HTTP server triggers local fallback
        res = get_assessment_analysis(input_dict)
        self.assertIn('prediction_code', res)
        self.assertIn('top_contributing_factors', res)
        self.assertIn('source', res)

if __name__ == "__main__":
    unittest.main()
