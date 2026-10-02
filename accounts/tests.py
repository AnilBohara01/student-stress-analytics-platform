from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.password = "ComplexPass123!"
        self.email = "testuser@example.com"
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def test_user_registration(self):
        reg_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'newuser@example.com',
            'password1': 'NewPass123!456',
            'password2': 'NewPass123!456'
        }
        response = self.client.post(reverse('accounts:register'), data=reg_data)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registration_duplicate_email(self):
        reg_data = {
            'username': 'anotheruser',
            'email': self.email,  # Duplicate email
            'password1': 'Pass123!456789',
            'password2': 'Pass123!456789'
        }
        response = self.client.post(reverse('accounts:register'), data=reg_data)
        self.assertEqual(response.status_code, 200)  # Form re-rendered with error
        self.assertFalse(User.objects.filter(username='anotheruser').exists())

    def test_user_login_and_logout(self):
        login_success = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login_success)

        logout_response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(logout_response.status_code, 302)

    def test_profile_view_protected(self):
        # Unauthenticated access
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Authenticated access
        self.client.login(username=self.username, password=self.password)
        profile_response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertContains(profile_response, self.username)
