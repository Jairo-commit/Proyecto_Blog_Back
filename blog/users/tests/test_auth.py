import pytest
from django.contrib.auth.models import User,Group
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from django.urls import reverse


@pytest.fixture
def createUsers(db):
    different_group = Group.objects.create(name="different_group")
    default_team = Group.objects.create(name="default_team")
    client=APIClient()
    user = User.objects.create_user(email="user1@test.com",
                                username="prueba1",
                                password="test_password1") 

    user.groups.add(default_team)

    return client,user

@pytest.fixture
def auth_tokens(createUsers):
    _, user = createUsers
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }

def test_obtain_token_valid_credentials(createUsers):
    url = reverse('token_obtain_pair')
    client, test_user = createUsers

    response = client.post(url, {
        'username': test_user.username,
        'password': 'test_password1'
    })
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data

def test_obtain_token_invalid_credentials(createUsers):
    url = reverse('token_obtain_pair')
    client, _ = createUsers
    response = client.post(url, {
        'username': 'wronguser',
        'password': 'wrongpass'
    })
    assert response.status_code == 401


def test_token_refresh(createUsers, auth_tokens):
    url = reverse('token_refresh')
    client, _ = createUsers
    response = client.post(url, {'refresh': auth_tokens['refresh']})
    assert response.status_code == 200
    assert 'access' in response.data

def test_get_current_user_authenticated(createUsers, auth_tokens):
    url = reverse('current_user')
    client, user = createUsers
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_tokens["access"]}')
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['username'] == user.username

def test_get_current_user_unauthenticated(createUsers):
    url = reverse('current_user')
    client, _ = createUsers
    response = client.get(url)
    assert response.status_code == 401

def test_logout_valid_refresh_token(createUsers, auth_tokens):
    url = reverse('logout')
    client, _ = createUsers
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_tokens["access"]}')
    response = client.post(url, {'refresh': auth_tokens['refresh']})
    assert response.status_code == 200

def test_logout_invalid_refresh_token(createUsers, auth_tokens):
    url = reverse('logout')
    client, _ = createUsers
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_tokens["access"]}')
    response = client.post(url, {'refresh': 'notavalidtoken'})
    assert response.status_code == 400

def test_get_current_user_authenticated(createUsers, auth_tokens):
    client, user = createUsers
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_tokens["access"]}')

    url = reverse('current_user')
    response = client.get(url)

    assert response.status_code == 200
    assert response.data['username'] == user.username
    assert response.data['id'] == user.id
    assert 'password' in response.data  # Aunque no es recomendable
    assert 'groups' in response.data
    assert isinstance(response.data['groups'], list)

def test_get_current_user_unauthenticated(createUsers):
    url = reverse('current_user')
    client, _ = createUsers
    response = client.get(url)

    assert response.status_code == 401