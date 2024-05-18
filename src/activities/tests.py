from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Guide
from django.contrib.auth import get_user_model

User = get_user_model()

class GuideViewSetTestCase(APITestCase):
    def setUp(self):
        self.guide = Guide.objects.create(name='Test Guide', bio='Test Bio', email='test@example.com')
        self.user = User.objects.create(username='test_user', email='test_user@example.com')
        self.admin = User.objects.create(username='test_admin', email='test_admin@example.com', is_admin=True)

    def test_list_guides(self):
        url = reverse('guides-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_guide(self):
        url = reverse('guides-detail', kwargs={'pk': self.guide.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Guide')


        
    def test_create_guide(self):
        url = reverse('guides-list')
        data = {'name': 'New Guide', 'bio': 'New Bio', 'email': 'new_guide@example.com'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Guide.objects.count(), 1)
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Guide.objects.count(), 2)

    def test_update_guide(self):
        url = reverse('guides-detail', kwargs={'pk': self.guide.pk})
        data = {'name': 'Updated Guide', 'bio': 'Updated Bio', 'email': 'updated_guide@example.com'}
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Guide')

    def test_delete_guide(self):
        url = reverse('guides-detail', kwargs={'pk': self.guide.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Guide.objects.count(), 1)
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Guide.objects.count(), 0)

class GuideLikeViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', email='test_user@example.com', password='testpass123')
        self.guide = Guide.objects.create(name='Test Guide', bio='Test Bio', email='test@example.com')
        self.client.force_authenticate(user=self.user)
        
    def test_guide_liked_by_user_field(self):
        toggle_url = reverse('guides-toggle-like', kwargs={'pk': self.guide.pk})
        self.client.post(toggle_url)
        detail_url = reverse('guides-detail', kwargs={'pk': self.guide.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        self.client.post(toggle_url)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])

    def test_guide_liked_by_user_field_unauthenticated(self):
        self.client.force_authenticate(user=None)
        detail_url = reverse('guides-detail', kwargs={'pk': self.guide.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])

    def test_toggle_like_unauthenticated(self):
        self.client.force_authenticate(user=None)
        toggle_url = reverse('guides-toggle-like', kwargs={'pk': self.guide.pk})
        response = self.client.post(toggle_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_toggle_like(self):
        url = reverse('guides-toggle-like', kwargs={'pk': self.guide.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])

    def test_toggle_like_unauthenticated(self):
        url = reverse('guides-toggle-like', kwargs={'pk': self.guide.pk})
        self.client.force_authenticate(user=None)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', response.data['detail'])
