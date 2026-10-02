from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from assessments.models import Assessment


class DashboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "analyticstudent"
        self.password = "SecurePass123!"
        self.user = User.objects.create_user(
            username=self.username,
            email="analytics@example.com",
            password=self.password
        )

    def test_dashboard_and_analytics_views(self):
        # 1. Unauthenticated access redirect
        home_resp = self.client.get(reverse('dashboard:home'))
        self.assertEqual(home_resp.status_code, 302)

        # 2. Login
        self.client.login(username=self.username, password=self.password)

        # 3. Create two sample assessments to test trends and deltas
        a1 = Assessment.objects.create(
            user=self.user,
            student_type='college',
            sleep_hours=6.0,
            study_hours=8.0,
            social_media_hours=3.0,
            attendance=80.0,
            exam_pressure=8.0,
            family_support=5.0,
            month=9,
            predicted_stress_level=1,
            predicted_label='High Stress',
            probability_low_stress=0.20,
            probability_high_stress=0.80
        )

        a2 = Assessment.objects.create(
            user=self.user,
            student_type='college',
            sleep_hours=7.5,
            study_hours=6.0,
            social_media_hours=2.0,
            attendance=90.0,
            exam_pressure=4.0,
            family_support=8.0,
            month=10,
            predicted_stress_level=0,
            predicted_label='Low/Normal Stress',
            probability_low_stress=0.85,
            probability_high_stress=0.15
        )

        # 4. Test Dashboard Home View
        home_auth_resp = self.client.get(reverse('dashboard:home'))
        self.assertEqual(home_auth_resp.status_code, 200)
        self.assertContains(home_auth_resp, "Student Analytics Dashboard")

        # 5. Test Analytics & Trends View
        analytics_resp = self.client.get(reverse('dashboard:analytics'))
        self.assertEqual(analytics_resp.status_code, 200)
        self.assertContains(analytics_resp, "Lifestyle Trends & Longitudinal Analytics")
        self.assertIn('deltas', analytics_resp.context)
        
        # Verify delta calculation (+1.5 hrs sleep increase)
        deltas = analytics_resp.context['deltas']
        self.assertAlmostEqual(deltas['sleep'], 1.5, places=1)
