from collections import ChainMap
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings, modify_settings
from faker import Faker

User = get_user_model()
faker = Faker()


@override_settings(DJOSER=ChainMap({'SEND_ACTIVATION_EMAIL': False}, settings.DJOSER))
class UserViewSetTest(APITestCase):

    def setUp(self):
        self.user_info = self.generate_user_info()
        
    def generate_user_info(self):
        
        password = faker.password()
        
        return {
            "first_name": faker.first_name(),
            "last_name": faker.last_name,
            "username": faker.user_name(),
            "email": faker.email(),
            "password": password,
            "re_password": password
        }
        
    def test_create_user(self):
        
        url = reverse("user-list")
        response = self.client.post(
            url,
            self.user_info,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        user = User.objects.get(id=response.data['id'])
        self.assertEqual(user.email, self.user_info["email"])
        self.assertEqual(user.username, self.user_info["username"])
        self.assertTrue(user.password is not self.user_info["password"])
        self.assertTrue(user.password is not None)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_admin is not True)
        self.assertTrue(user.is_superuser is not True)
        self.assertTrue(user.is_staff is not True)
        
    def test_create_jwt_token(self):
        new_user = self.client.post(
            reverse("user-list"),
            self.user_info,
        )
        self.assertEqual(new_user.status_code, status.HTTP_201_CREATED)
        
        url = reverse("jwt-create")
        data = {
            "email": self.user_info["email"],
            "password": self.user_info["password"],
        }
        response = self.client.post(url, data)

        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["access"] is not None)

    def test_get_current_user(self):

        new_user = self.client.post(
            reverse("user-list"),
            self.user_info,
        )
        self.assertEqual(new_user.status_code, status.HTTP_201_CREATED)
        
        url = reverse("jwt-create")
        data = {
            "email": self.user_info["email"],
            "password": self.user_info["password"],
        }

        response = self.client.post(url, data)
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["access"] is not None)

        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {token}")

        url = reverse('user-me')
        get_user = self.client.get(url)

        self.assertEqual(get_user.status_code, status.HTTP_200_OK)
        self.assertEqual(get_user.data["id"], new_user.data["id"])
        self.assertEqual(get_user.data["email"], new_user.data["email"])

        test_user = self.client.post(
            reverse("user-list"),
            self.generate_user_info(),
        )
        test_id = test_user.data['id']
        
        url = reverse('user-list') + "/{test_id}/"
        get_user = self.client.get(url)
        self.assertEqual(get_user.status_code, status.HTTP_404_NOT_FOUND)
