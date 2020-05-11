from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from assistance import models


# Create your tests here.
class UserViewSetTestCase(APITestCase):
    def setUp(self):
        self.create_users()

    def create_users(self):
        """
        Create `piero` and `admin` Users.

            piero: non-admin user.
            admin: admin user.
        """
        User.objects.create_user(
            username='non_admin',
            first_name='Piero',
            last_name='Narciso',
            password='12345',
            email='piero@gmail.com'
        )
        User.objects.create_superuser(
            username='admin',
            first_name='Admin',
            last_name='Admin',
            password='12345',
            email='admin@gmail.com'
        )

    def test_user_count(self):
        count = User.objects.count()
        self.assertEqual(count, 2)

    def test_signup(self):
        url = '/api/users/'
        data = {
            'username': 'PieroN',
            'first_name': 'Piero',
            'last_name': 'Narciso',
            'password': '12345',
            'email': 'pieroN@gmail.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_login(self):
        url = '/api/login-token/'
        data = {
            'username': 'non_admin',
            'password': '12345'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('login'), True)

    def test_prohibited_user(self):
        url = '/api/users/get_user_data/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_data(self):
        url = '/api/users/get_user_data/'
        user = User.objects.get(username='non_admin')
        self.client.force_authenticate(user=user)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), 'non_admin')


class NumCodeViewSet(APITestCase):
    def setUp(self):
        UserViewSetTestCase().create_users()
        self.url = '/api/codes/'

    def create_num_code(self):
        models.NumCode.objects.create()

    def test_num_code_count(self):
        self.create_num_code()
        count = models.NumCode.objects.count()
        self.assertEqual(count, 1)

    def test_num_code_create_admin(self):
        self.create_num_code()
        url = self.url
        user = User.objects.get(username='admin')
        self.client.force_authenticate(user=user)
        response = self.client.post(url, format='json')
        # Just one code, the rest is eliminated
        count = models.NumCode.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(count, 1)

    def test_num_code_create_non_admin(self):
        self.create_num_code()
        url = self.url
        user = User.objects.get(username='non_admin')
        self.client.force_authenticate(user=user)
        response = self.client.post(url, format='json')
        # One code
        count = models.NumCode.objects.count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_code_admin(self):
        self.create_num_code()
        url = self.url + 'get_code/'
        user = User.objects.get(username='admin')
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_code_non_admin(self):
        self.create_num_code()
        url = self.url + 'get_code/'
        user = User.objects.get(username='non_admin')
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AssistanceViewSet(APITestCase):
    def setUp(self):
        UserViewSetTestCase().create_users()
        NumCodeViewSet().create_num_code()
        self.url = '/api/assistances/'

    def create_assistances(self):
        models.Assistance.objects.create(
            user=User.objects.get(username='non_admin')
        )

    def test_assistance_count(self):
        self.create_assistances()
        count = models.Assistance.objects.count()
        self.assertEqual(count, 1)

    def test_assistance_create(self):
        url = self.url
        user = User.objects.get(username='non_admin')
        self.client.force_authenticate(user=user)
        code = models.NumCode.objects.last().code
        data = {'code': code}
        response = self.client.post(url, data, format='json')
        count = models.Assistance.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(count, 1)

    def test_assistance_get_today(self):
        self.create_assistances()
        url = self.url + 'get_today/'
        user = User.objects.get(username='admin')
        self.client.force_authenticate(user=user)
        response = self.client.get(url, formt='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
