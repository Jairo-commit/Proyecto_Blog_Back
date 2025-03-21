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

    assert response.status_code == 200                      #Test Redirect to login page
    assert not unauthenticated_user.is_authenticated


# def test_logout(ClientUser):
#     client, _ = ClientUser
#     response = client.post("/user/api-auth/login/", {"username": "testuser@test.com", "password": "test_password"},follow=True)
#     assert "_auth_user_id" in client.session                        #Login First

#     response = client.post("/user/api-auth/logout/", follow=True)   #Logout
#     assert response.status_code == 200                              #Test Redirect
#     assert "_auth_user_id" not in client.session                    #Test Unlog"""