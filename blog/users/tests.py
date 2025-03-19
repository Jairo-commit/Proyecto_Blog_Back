from django.test import TestCase
from django.contrib.auth.models import User

from django.urls import reverse
from rest_framework import status
# Create your tests here.

class RegisterTestCase(TestCase):
    def test_registro_exitoso(self):
        data = {
            'username': 'test',
            'password': 'test1234',
            'first_name': 'nombre',
            'last_name': 'apellido',
            'email': 'example@example.com'
        }
        response = self.client.post(reverse('user_register-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'test')
        self.assertTrue(User.objects.get().check_password('test1234'))

        data = {
        'username': 'test1',
        'password': 'test1234',
        'first_name': '',
        'last_name': 'apellido',
        'email': 'example@example.com'
        }
        response = self.client.post(reverse('user_register-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            'username': 'test2',
            'password': 'test1234',
            'first_name': 'nombre',
            'last_name': '',
            'email': 'example@example.com'
        }
        response = self.client.post(reverse('user_register-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            'username': 'test3',
            'password': 'test1234',
            'first_name': 'nombre',
            'last_name': 'apellido',
            'email': ''
        }
        response = self.client.post(reverse('user_register-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_registro_fallido(self):
        data = {
            'username': '',
            'password': 'test1234',
            'first_name': 'nombre',
            'last_name': 'apellido',
            'email': 'example@example.com'
        }
        response = self.client.post(reverse('user_register-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            'username': 'test',
            'password': '',
            'first_name': 'nombre',
            'last_name': 'apellido',
            'email': 'example@example.com'
        }
        response = self.client.post(reverse('user_register-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)