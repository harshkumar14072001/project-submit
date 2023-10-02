from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import File

User = get_user_model()

class FileSharingSystemTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Ops User
        self.ops_user = User.objects.create_user(
            username='opsuser',
            password='password',
            is_ops_user=True
        )

        # Create Client User
        self.client_user = User.objects.create_user(
            username='clientuser',
            password='password'
        )

        # Login Ops User
        self.client.login(username='opsuser', password='password')

    def test_file_upload(self):
        response = self.client.post(
            '/files/upload_file/',
            data={'file': 'testfile.pptx'},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_file_upload(self):
        response = self.client.post(
            '/files/upload_file/',
            data={'file': 'invalidfile.txt'},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_file_list(self):
        response = self.client.get('/files/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_file_download(self):
        file = File.objects.create(owner=self.ops_user, file='testfile.pptx')
        permission = file.filepermission_set.create(user=self.client_user, encrypted_url='randomurl')
        
        response = self.client.get(f'/files/download_file/{permission.encrypted_url}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthorized_file_download(self):
        file = File.objects.create(owner=self.ops_user, file='testfile.pptx')
        permission = file.filepermission_set.create(user=self.client_user, encrypted_url='randomurl') #url can be random
        
        self.client.logout()  # Logging out Ops User
        response = self.client.get(f'/files/download_file/{permission.encrypted_url}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login(self):
        response = self.client.post(
            '/users/login/',
            data={'username': 'clientuser', 'password': 'password'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        response = self.client.post('/users/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
