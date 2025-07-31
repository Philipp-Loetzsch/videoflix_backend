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
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )
        
        # Create test video file
        self.video_file = tempfile.NamedTemporaryFile(suffix='.mp4').name
        with open(self.video_file, 'wb') as f:
            f.write(b'fake video content')
            
        # Create a simple valid JPEG image for thumbnail
        from PIL import Image
        import io
        
        # Create a small red image
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        self.thumbnail_content = img_io.getvalue()
        
        # Save it to a temporary file
        self.thumbnail_file = tempfile.NamedTemporaryFile(suffix='.jpg').name
        with open(self.thumbnail_file, 'wb') as f:
            f.write(self.thumbnail_content)

        # Create a test video
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

    def tearDown(self):
        # Clean up temp files
        try:
            os.remove(self.video_file)
            os.remove(self.thumbnail_file)
        except:
            pass

    def test_list_videos_authenticated(self):
        """Test that authenticated users can list videos"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('content_app:video-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_list_videos_unauthenticated(self):
        """Test that unauthenticated users cannot list videos"""
        url = reverse('content_app:video-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_video_as_admin(self):
        """Test that admin users can create videos"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('content_app:video-list')
        
        with open(self.video_file, 'rb') as video_file, \
             open(self.thumbnail_file, 'rb') as thumbnail_file:
            
            # Read the thumbnail file content
            with open(self.thumbnail_file, 'rb') as thumbnail_file:
                data = {
                    'title': 'New Test Video',
                    'description': 'New Test Description',
                    'file': video_file,
                    'thumbnail': SimpleUploadedFile('test.jpg', self.thumbnail_content),
                    'preview': SimpleUploadedFile('preview.mp4', b'fake preview content'),
                    'preview_title': 'New Preview',
                    'category': 'Action'
                }
            response = self.client.post(url, data, format='multipart')
            
            if response.status_code != status.HTTP_201_CREATED:
                print("Error response:", response.data)  # Debug output
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Video.objects.count(), 2)

    def test_create_video_as_regular_user(self):
        """Test that regular users cannot create videos"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('content_app:video-list')
        
        with open(self.video_file, 'rb') as video_file:
            data = {
                'title': 'New Test Video',
                'description': 'New Test Description',
                'file': video_file,
                'category': 'Action'
            }
            response = self.client.post(url, data, format='multipart')
            
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_video(self):
        """Test retrieving a specific video"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('content_app:video-detail', kwargs={'pk': self.video.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Video')

    def test_update_video_as_admin(self):
        """Test that admin users can update videos"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('content_app:video-detail', kwargs={'pk': self.video.pk})
        data = {
            'title': 'Updated Test Video',
            'description': 'Updated Description',
            'category': 'Horror'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Video.objects.get(pk=self.video.pk).title, 'Updated Test Video')

    def test_update_video_as_regular_user(self):
        """Test that regular users cannot update videos"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('content_app:video-detail', kwargs={'pk': self.video.pk})
        data = {
            'title': 'Updated Test Video',
            'description': 'Updated Description'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_video_as_admin(self):
        """Test that admin users can delete videos"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('content_app:video-detail', kwargs={'pk': self.video.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Video.objects.count(), 0)

    def test_delete_video_as_regular_user(self):
        """Test that regular users cannot delete videos"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('content_app:video-detail', kwargs={'pk': self.video.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
