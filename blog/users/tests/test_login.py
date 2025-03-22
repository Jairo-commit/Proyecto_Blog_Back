import pytest
import json
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

from test_setup_users import createUsers
from posts.models import BlogPost

#Create Login & Unlog User Views--------------------------------------------------------------------------------------------------------------------------

def test_login_view(createUsers):
    client, user = createUsers
    response = client.post(reverse("rest_framework:login"), {"username": "prueba1", "password": "test_password1"},follow=True)
    authenticated_user = get_user(client)             

    assert response.status_code == status.HTTP_200_OK           #Test Redirect to post page
    assert response.request["PATH_INFO"] == "/api/post/"
    assert authenticated_user.is_authenticated        #Test Auth
    assert authenticated_user.id == user.id
    assert "_auth_user_id" in client.session 

def test_login_view_fail(createUsers):
    client, _ = createUsers
    response = client.post(reverse("rest_framework:login"), {"username": "prueba1", "password": "test_password21"},follow=True)
    unauthenticated_user = get_user(client)             

    assert response.status_code == status.HTTP_200_OK 
    assert response.request["PATH_INFO"] == reverse("rest_framework:login")               
    assert not unauthenticated_user.is_authenticated


def test_logout(createUsers):
    client, _ = createUsers
    response = client.post(reverse("rest_framework:login"), {"username": "prueba1", "password": "test_password1"},follow=True)
    assert "_auth_user_id" in client.session                        #Login First
     

    response = client.post(reverse("rest_framework:logout"), follow=True)   
    unauthenticated_user = get_user(client) 
    assert response.status_code == status.HTTP_200_OK                              
    assert response.request["PATH_INFO"] == reverse("rest_framework:logout") 
    assert not unauthenticated_user.is_authenticated                

#Resgister tests----------------------------------------------------------------------------------------------------------------------------

def test_success_register(createUsers):
        
        client,_ = createUsers
        data = {
            'username': 'test',
            'password': 'test1234',
            'first_name': 'nombre',
            'last_name': 'apellido',
            'email': 'example@example.com'
        }
        response = client.post(reverse('user_register-list'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.count() == 2
        user = User.objects.filter(username="test").first()
        assert user is not None, "User not found"
        assert user.username == "test"
        assert user.check_password("test1234")

def test_success_register_info_incomplete(createUsers):
        
        client,_ = createUsers
        
        data = {
        'username': 'test1',
        'password': 'test1234',
        'first_name': '',
        'last_name': 'apellido',
        'email': 'example@example.com'
        }
        response = client.post(reverse('user_register-list'), data)
        assert response.status_code == status.HTTP_201_CREATED

        data = {
            'username': 'test2',
            'password': 'test1234',
            'first_name': 'nombre',
            'last_name': '',
            'email': 'example@example.com'
        }
        response = client.post(reverse('user_register-list'), data)
        assert response.status_code == status.HTTP_201_CREATED

        data = {
            'username': 'test3',
            'password': 'test1234',
            'first_name': 'nombre',
            'last_name': 'apellido',
            'email': ''
        }
        response = client.post(reverse('user_register-list'), data)
        assert response.status_code == status.HTTP_201_CREATED

def test_unsuccess_register(createUsers):
        
        client,_ = createUsers
        
        data = {
        'username': 'test1',
        'password': 'test1234',
        'first_name': '',
        'last_name': 'apellido',
        'email': 'example@example.com',
        'is_staff': True
        }
        response = client.post(reverse('user_register-list'), data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST