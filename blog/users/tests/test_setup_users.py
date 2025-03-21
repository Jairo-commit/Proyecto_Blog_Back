import pytest
import json
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group


@pytest.fixture
def createUsers(db):
    different_group = Group.objects.create(name="different_group")
    default_team = Group.objects.create(name="default_team")
    client=APIClient()
    user = User.objects.create_user(email="user1@test.com",
                                username="prueba1",
                                password="test_password1")  # ✅ Encripta la contraseña correctamente

    user.groups.add(default_team)

    return client,user