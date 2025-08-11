from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Video
from django.contrib.auth import get_user_model
import tempfile
import os

User = get_user_model()

class VideoTests(APITestCase):
    """Test suite for Video API endpoints."""
    def setUp(self):
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )
        
        from PIL import Image
        import io
        
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        self.thumbnail_content = img_io.getvalue()
        
        self.video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            file=SimpleUploadedFile('test.mp4', b'fake video content'),
            thumbnail=SimpleUploadedFile('test.jpg', self.thumbnail_content),
            preview=SimpleUploadedFile('preview.mp4', b'fake preview content'),
            preview_title='Test Preview',
            category='Action',
            duration=120
        )

    def test_list_videos_authenticated(self):
        """Test that authenticated users can list videos."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('content_app:video-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_list_videos_unauthenticated(self):
        """Test that unauthenticated users cannot list videos."""
        url = reverse('content_app:video-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_video(self):
        """Test retrieving a specific video."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('content_app:video-detail', kwargs={'pk': self.video.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Video')

    def test_create_video_not_allowed(self):
        """Test that video creation is not allowed through the API."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('content_app:video-list')
        data = {
            'title': 'New Test Video',
            'description': 'New Test Description',
            'category': 'Action'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_video_not_allowed(self):
        """Test that video updates are not allowed through the API."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('content_app:video-detail', kwargs={'pk': self.video.pk})
        data = {
            'title': 'Updated Test Video',
            'description': 'Updated Description'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_video_not_allowed(self):
        """Test that video deletion is not allowed through the API."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('content_app:video-detail', kwargs={'pk': self.video.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_video_url_is_https(self):
        """Test that video URLs are returned as HTTPS."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('content_app:video-detail', kwargs={'pk': self.video.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'file' in response.data and response.data['file']:
            self.assertTrue(response.data['file'].startswith('https://'))
