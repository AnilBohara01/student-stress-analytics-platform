from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Assessment


class AssessmentBackendTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "teststudent"
        self.password = "SecurePass123!"
        self.user = User.objects.create_user(
            username=self.username,
            email="student@example.com",
            password=self.password
        )

    def test_assessment_creation_and_ml_inference(self):
        # 1. Login
        login_success = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login_success)

        # 2. Post New Assessment
        form_data = {
            'student_type': 'college',
            'sleep_hours': 5.5,
            'study_hours': 7.0,
            'social_media_hours': 4.0,
            'attendance': 75.0,
            'exam_pressure': 8.5,
            'family_support': 3.5,
            'month': 10,
        }

        response = self.client.post(reverse('assessments:new'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect to result page

        # 3. Verify Database Record Created
        assessment = Assessment.objects.filter(user=self.user).first()
        self.assertIsNotNone(assessment)
        self.assertIn(assessment.predicted_stress_level, [0, 1])
        self.assertIn(assessment.predicted_label, ["Low/Normal Stress", "High Stress"])
        self.assertGreater(len(assessment.top_contributing_factors), 0)
        self.assertTrue(len(assessment.narrative_explanation) > 0)
        self.assertEqual(assessment.model_version, "stresslens_v1.0.0")

        # 4. Check Detail View
        detail_response = self.client.get(reverse('assessments:detail', kwargs={'pk': assessment.pk}))
        self.assertEqual(detail_response.status_code, 200)

        # 5. Check History View
        history_response = self.client.get(reverse('assessments:history'))
        self.assertEqual(history_response.status_code, 200)
        self.assertContains(history_response, assessment.predicted_label)

        # 6. Check PDF Report Export Stream
        pdf_response = self.client.get(reverse('assessments:export_pdf', kwargs={'pk': assessment.pk}))
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
        self.assertTrue(len(pdf_response.content) > 1000)  # Valid non-empty PDF byte stream

