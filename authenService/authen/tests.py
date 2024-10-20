from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from users import models


class SignUpViewTest(APITestCase):
    def setUp(self):
        self.valid_payload = {
            'username': "user0",
            'password': "user0password",
            'first_name': "User",
            'last_name': "Test"
        }

        self.invalid_payload_missing_username_field = {
            'password': "user0password",
            'first_name': "User",
            'last_name': "Test"
        }

        self.existing_user = models.User.objects.create(
            username="user1",
            password="user1password",
            first_name="User",
            last_name="Test"
        )

        self.invalid_payload_existing_username = {
            'username': "user1",
            'password': "user1password",
            'first_name': "User",
            'last_name': "Test"
        }

        self.url = reverse('signup')

    def test_create_user_valid_payload(self):
        response = self.client.post(self.url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('detail', response.data)
        self.assertEqual(models.User.objects.count(), 2)

    def test_create_user_invalid_payload_missing_username_field(self):
        response = self.client.post(self.url, self.invalid_payload_missing_username_field, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertEqual(models.User.objects.count(), 1)
    
    def test_create_user_existing_username(self):
        response = self.client.post(self.url, self.invalid_payload_existing_username, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertEqual(models.User.objects.count(), 1)


class SignInViewTest(APITestCase):
    def setUp(self):
        self.existing_user = models.User.objects.create(
            username="user0",
            password="user0password",
            first_name="User",
            last_name="Test"
        )

        self.url = reverse('signin')

    def test_sign_in_success(self):
        response = self.client.post(self.url, {'username': 'user0', 'password': 'user0password'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', response.data)

    def test_sign_in_invalid_credentials(self):
        response = self.client.post(self.url, {'username': 'userUnknown', 'password': 'userUnknownPassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Invalid credentials.')