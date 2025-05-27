import pytest
import json
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group
from django.urls import reverse

from posts.models import BlogPost
from interactions.models import Like

@pytest.fixture
def createUsers(db):
    different_group = Group.objects.create(name="different_group")
    default_team = Group.objects.create(name="default_team")
    client=APIClient()
    user1 = User.objects.create(email="user1@test.com",
                            username="prueba1",
                            password="test_password1",
                            )
    user1.groups.add(default_team)
    user2 = User.objects.create(email="user2@test.com",
                            username="prueba2",
                            password="test_password2",
                            )
    user2.groups.add(default_team) 
    user3 = User.objects.create(email="user3@test.com",
                            username="prueba3",
                            password="test_password3",
                            )
    user3.groups.add(different_group)
    user4 = User.objects.create(email="user5@test.com",
                            username="prueba4",
                            password="test_password4",
                            is_staff=True
                            )
    user4.groups.add(different_group)
    return client,user1,user2,user3,user4

@pytest.fixture
def post_prueba(createUsers):
    client,user1,_,_,_ = createUsers

    client.force_authenticate(user=user1)

    # Datos del nuevo post
    postdata = {
        "title": "Post de prueba para loggueados",
        "content": "You gotta be logged in",
        "public_access": "None",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }

    client.post(reverse("blogpost-list"), json.dumps(postdata), content_type="application/json")

    return BlogPost.objects.get(title="Post de prueba para loggueados")

@pytest.fixture
def post_prueba_read_public_access(createUsers):
    client,user1,_,_,_ = createUsers

    client.force_authenticate(user=user1)

    # Datos del nuevo post
    postdata = {
        "title": "Post de prueba para loggueados",
        "content": "You gotta be logged in",
        "public_access": "Read",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }

    client.post(reverse("blogpost-list"), json.dumps(postdata), content_type="application/json")

    return BlogPost.objects.get(title="Post de prueba para loggueados")

@pytest.fixture
def post_prueba_with_likes_and_comments(createUsers):
    client, user1, user2, user3, user4 = createUsers

    client.force_authenticate(user=user1)

    # Datos del nuevo post
    postdata = {
        "title": "Post de prueba para loggueados solo lectura",
        "content": "This post can be read by people who is loggued",
        "public_access": "Read",
        "authenticated_access": "Read",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }
    data_comment = {"content": "Esto es un test"}

    # 🔹 Crear el post y guardar la respuesta
    response = client.post(reverse("blogpost-list"), json.dumps(postdata), content_type="application/json")

    assert response.status_code == 201  # ✅ Asegurar que el post se creó correctamente

    # 🔹 Extraer el ID del post recién creado
    post_id = response.json()["id"]

    # 🔹 Usuarios dando "like" al post
    for user in [user1, user2, user3, user4]:
        client.force_authenticate(user=user)
        response_like = client.post(reverse("blogpost-giving-like", kwargs={"pk": post_id}))
        response_comment = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_id}), data_comment)
        assert response_like.status_code == 200  # ✅ Asegurar que la petición fue exitosa
        assert response_comment.status_code == 201

    # 🔹 Verificar que el post tiene 4 likes
    post = BlogPost.objects.get(id=post_id)
    like_count = Like.objects.filter(post=post).count()
    
    assert like_count == 4, f"Se esperaban 4 likes, pero se encontraron {like_count}."

    return post  # ✅ Retornar el post si todo es correcto

@pytest.fixture
def post_prueba_none_authenticated_access(createUsers):
    client,user1,_,_,_ = createUsers

    client.force_authenticate(user=user1)

    # Datos del nuevo post
    postdata = {
        "title": "Post de prueba para el grupo",
        "content": "This post can be edit for the team, but It can't be read by authenticated people",
        "public_access": "None",
        "authenticated_access": "None",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }

    client.post(reverse("blogpost-list"), json.dumps(postdata), content_type="application/json")

    return BlogPost.objects.get(title="Post de prueba para el grupo")

@pytest.fixture
def post_prueba_read_only_access(createUsers):
    client,user1,_,_,_ = createUsers

    client.force_authenticate(user=user1)

    # Datos del nuevo post
    postdata = {
        "title": "Post de prueba para el grupo",
        "content": "This post can be edit for the team, but It can't be read by authenticated people",
        "public_access": "None",
        "authenticated_access": "Read",
        "group_access": "Read",
        "author_access": "Read and Edit",
    }

    client.post(reverse("blogpost-list"), json.dumps(postdata), content_type="application/json")

    return BlogPost.objects.get(title="Post de prueba para el grupo")

@pytest.fixture
def post_prueba_only_author(createUsers):
    client,user1,_,_,_ = createUsers

    client.force_authenticate(user=user1)

    # Datos del nuevo post
    postdata = {
        "title": "Post de prueba para el grupo",
        "content": "This post can be edit for the team, but It can't be read by authenticated people",
        "public_access": "None",
        "authenticated_access": "None",
        "group_access": "None",
        "author_access": "Read and Edit",
    }

    client.post(reverse("blogpost-list"), json.dumps(postdata), content_type="application/json")

    return BlogPost.objects.get(title="Post de prueba para el grupo")

@pytest.fixture
def post_prueba_with_likes_and_comments_privado(createUsers):
    client, user1, user2, user3, user4 = createUsers

    client.force_authenticate(user=user1)

    # Datos del nuevo post
    postdata = {
        "title": "Post de prueba para loggueados solo lectura",
        "content": "This post can be read by people who is loggued",
        "public_access": "None",
        "authenticated_access": "None",
        "group_access": "None",
        "author_access": "Read and Edit",
    }
    data_comment = {"content": "Esto es un test"}

    # 🔹 Crear el post y guardar la respuesta
    response = client.post(reverse("blogpost-list"), json.dumps(postdata), content_type="application/json")

    assert response.status_code == 201  # ✅ Asegurar que el post se creó correctamente

    # 🔹 Extraer el ID del post recién creado
    post_id = response.json()["id"]

    response_like = client.post(reverse("blogpost-giving-like", kwargs={"pk": post_id}))
    response_comment = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_id}), data_comment)
    assert response_like.status_code == 200  # ✅ Asegurar que la petición fue exitosa
    assert response_comment.status_code == 201

    # 🔹 Verificar que el post tiene 1 likes
    post = BlogPost.objects.get(id=post_id)
    like_count = Like.objects.filter(post=post).count()

    assert like_count == 1, f"Se esperaban 1 like, pero se encontraron {like_count}."

    return post  # ✅ Retornar el post si todo es correcto

@pytest.fixture
def post_prueba_with_likes_and_comments_group_access(createUsers):
    client, user1, user2, user3, user4 = createUsers

    client.force_authenticate(user=user1)

    # Datos del nuevo post
    postdata = {
        "title": "Post de prueba para loggueados solo lectura",
        "content": "This post can be read by people who is loggued",
        "public_access": "None",
        "authenticated_access": "None",
        "group_access": "Read",
        "author_access": "Read and Edit",
    }
    data_comment = {"content": "Esto es un test"}

    # 🔹 Crear el post y guardar la respuesta
    response = client.post(reverse("blogpost-list"), json.dumps(postdata), content_type="application/json")

    assert response.status_code == 201  # ✅ Asegurar que el post se creó correctamente

    # 🔹 Extraer el ID del post recién creado
    post_id = response.json()["id"]

    response_like = client.post(reverse("blogpost-giving-like", kwargs={"pk": post_id}))
    response_comment = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_id}), data_comment)
    assert response_like.status_code == 200  # ✅ Asegurar que la petición fue exitosa
    assert response_comment.status_code == 201

    post = BlogPost.objects.get(id=post_id)
    like_count = Like.objects.filter(post=post).count()

    assert like_count == 1, f"Se esperaban 1 like, pero se encontraron {like_count}."

    return post  # ✅ Retornar el post si todo es correcto

@pytest.fixture
def post_prueba_with_likes_and_comments_authenticated_access(createUsers):
    client, user1, user2, user3, user4 = createUsers

    client.force_authenticate(user=user1)

    # Datos del nuevo post
    postdata = {
        "title": "Post de prueba para loggueados solo lectura",
        "content": "This post can be read by people who is loggued",
        "public_access": "None",
        "authenticated_access": "Read",
        "group_access": "Read",
        "author_access": "Read and Edit",
    }
    data_comment = {"content": "Esto es un test"}

    # 🔹 Crear el post y guardar la respuesta
    response = client.post(reverse("blogpost-list"), json.dumps(postdata), content_type="application/json")

    assert response.status_code == 201  # ✅ Asegurar que el post se creó correctamente

    # 🔹 Extraer el ID del post recién creado
    post_id = response.json()["id"]

    response_like = client.post(reverse("blogpost-giving-like", kwargs={"pk": post_id}))
    response_comment = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_id}), data_comment)
    assert response_like.status_code == 200  # ✅ Asegurar que la petición fue exitosa
    assert response_comment.status_code == 201

    post = BlogPost.objects.get(id=post_id)
    like_count = Like.objects.filter(post=post).count()

    assert like_count == 1, f"Se esperaban 1 like, pero se encontraron {like_count}."

    return post  # ✅ Retornar el post si todo es correcto

