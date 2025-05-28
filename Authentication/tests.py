from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser

class AuthTests(APITestCase):
    def test_registration(self):
        url = reverse('register')
        data = {
            "email": "testuser@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email="testuser@example.com").exists())

    def test_login_unverified(self):
        user = CustomUser.objects.create_user(
            email="unverified@example.com",
            password="TestPass123!",
            is_active=True,
            email_verified=False
        )
        url = reverse('login')
        data = {"email": "unverified@example.com", "password": "TestPass123!"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn("Please verify your email", response.data['error'])

    def test_login_verified(self):
        user = CustomUser.objects.create_user(
            email="verified@example.com",
            password="TestPass123!",
            is_active=True,
            email_verified=True
        )
        url = reverse('login')
        data = {"email": "verified@example.com", "password": "TestPass123!"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], "verified@example.com")