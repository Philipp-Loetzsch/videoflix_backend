from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class UserAuthenticationTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "repeated_password": "testpass123"
        }
        self.user = User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="existing123"
        )
        self.user.is_active = True
        self.user.save()

    def test_register_user(self):
        url = reverse('user_app:register')
        response = self.client.post(url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_check_user_exists(self):
        url = reverse('user_app:check')
        response = self.client.post(url, {'email': 'existing@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)

    def test_user_login(self):
        url = reverse('user_app:login')
        login_data = {
            'email': 'existing@example.com',
            'password': 'existing123'
        }
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access_token' in response.cookies)
        self.assertTrue('refresh_token' in response.cookies)

    def test_user_activation(self):
        # Create an inactive user
        inactive_user = User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="inactive123"
        )
        inactive_user.is_active = False
        inactive_user.save()

        # Generate activation token
        uidb64 = urlsafe_base64_encode(force_bytes(inactive_user.pk))
        token = default_token_generator.make_token(inactive_user)
        
        url = reverse('user_app:activate', kwargs={'uidb64': uidb64, 'token': token})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        inactive_user.refresh_from_db()
        self.assertTrue(inactive_user.is_active)

    def test_forgot_password(self):
        url = reverse('user_app:password-reset')
        response = self.client.post(url, {'email': 'existing@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password(self):
        # Create activation token for password reset
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        url = reverse('user_app:password-confirm', kwargs={'uidb64': uidb64, 'token': token})
        data = {
            'new_password': 'newpass123',
            'repeated_new_password': 'newpass123'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    def test_token_refresh(self):
        # First login to get the refresh token
        login_url = reverse('user_app:login')
        login_data = {
            'email': 'existing@example.com',
            'password': 'existing123'
        }
        login_response = self.client.post(login_url, login_data)
        
        # Try to refresh the token
        refresh_url = reverse('user_app:token_refresh')
        response = self.client.post(refresh_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access_token' in response.cookies)

    def test_logout(self):
        # First login to get the tokens
        login_url = reverse('user_app:login')
        login_data = {
            'email': 'existing@example.com',
            'password': 'existing123'
        }
        self.client.post(login_url, login_data)
        
        # Then try to logout
        url = reverse('user_app:logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the refresh_token cookie is either not present or empty
        self.assertTrue('refresh_token' not in response.cookies or 
                       not response.cookies['refresh_token'].value)
