import pytest
import json
from django.urls import reverse
from rest_framework import status

from test_setup_interactions import createUsers, post_prueba_with_likes_and_comments_authenticated_access, post_prueba_with_likes_and_comments_privado, post_prueba_with_likes_and_comments_group_access,post_prueba_read_public_access, post_prueba_only_author, post_prueba_with_likes_and_comments, post_prueba_read_only_access
from interactions.models import Like, Comment

#Testing comments on a post --------------------------------------------------------------------------------------------------------------------

def test_giving_like_author_only(createUsers,post_prueba_read_public_access):

    client,user1,_,_,_ = createUsers
    client.force_authenticate(user=user1)

    # Ensure there are no likes before the request
    assert Like.objects.filter(post=post_prueba_read_public_access, user=user1).count() == 0

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_200_OK 

    # Ensure the like was created
    assert Like.objects.filter(post=post_prueba_read_public_access, user=user1).count() == 1

def test_giving_like_read_access(createUsers,post_prueba_read_only_access):

    client,_,user2,user3,_ = createUsers
    client.force_authenticate(user=user2)

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_read_only_access.id}))
    assert response.status_code == status.HTTP_200_OK 

    client.force_authenticate(user=user3)

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_read_only_access.id}))
    assert response.status_code == status.HTTP_200_OK 

def test_giving_like_read_and_edit_access(createUsers,post_prueba_read_public_access):

    client,_,user2,user3,_ = createUsers

    client.force_authenticate(user=None)

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    client.force_authenticate(user=user2)

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_200_OK 

    client.force_authenticate(user=user3)

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_200_OK 

def test_giving_like_twice(createUsers,post_prueba_read_public_access):

    client,user1,_,_,_ = createUsers
    client.force_authenticate(user=user1)

    # Ensure there are no likes before the request
    assert Like.objects.filter(post=post_prueba_read_public_access, user=user1).count() == 0

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_200_OK 
    
    # Ensure the like was created
    assert Like.objects.filter(post=post_prueba_read_public_access, user=user1).count() == 1

    # Try liking the post again (should fail because of unique_together)
    response_duplicate = client.post(reverse("blogpost-giving-like", kwargs={"pk": post_prueba_read_public_access.id}))

    # Assert that the second like attempt
    assert response_duplicate.status_code == status.HTTP_200_OK

    # Ensure there are no likes after the second request
    assert Like.objects.filter(post=post_prueba_read_public_access, user=user1).count() == 0

def test_giving_like_anonymous(createUsers,post_prueba_read_public_access):

    client,_,_,_,_ = createUsers

    client.force_authenticate(user=None)

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_giving_like_post_cannot_read(createUsers,post_prueba_only_author):

    client,_,user2,user3,_ = createUsers
    client.force_authenticate(user=user3) #No está ni en el equipo

    # Ensure there are no likes before the request
    assert Like.objects.filter(post=post_prueba_only_author, user=user3).count() == 0

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_only_author.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Ensure the like was no created
    assert Like.objects.filter(post=post_prueba_only_author, user=user3).count() == 0

    client.force_authenticate(user=user2)  #No está ni en el equipo
    # Ensure there are no likes before the request
    assert Like.objects.filter(post=post_prueba_only_author, user=user2).count() == 0 

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_only_author.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Ensure the like was no created
    assert Like.objects.filter(post=post_prueba_only_author, user=user2).count() == 0

def test_list_likes_of_post(createUsers,post_prueba_with_likes_and_comments):
    client,_,user2,user3,_ = createUsers

    client.force_authenticate(user=None)

    response = client.get(reverse("blogpost-list-likes",kwargs={"pk": post_prueba_with_likes_and_comments.id}))
    assert response.status_code == status.HTTP_200_OK 

    response_data = response.json()  # ✅ Obtiene el contenido JSON de la respuesta
    assert response_data["total_count"] == 4  # ✅ Asegura que hay 4 likes en la lista


    client.force_authenticate(user=user2)

    response = client.get(reverse("blogpost-list-likes",kwargs={"pk": post_prueba_with_likes_and_comments.id}))
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()  # ✅ Obtiene el contenido JSON de la respuesta
    assert response_data["total_count"] == 4  # ✅ Asegura que hay 4 likes en la lista

    client.force_authenticate(user=user3)

    response = client.get(reverse("blogpost-list-likes",kwargs={"pk": post_prueba_with_likes_and_comments.id}))
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()  # ✅ Obtiene el contenido JSON de la respuesta
    assert response_data["total_count"] == 4  # ✅ Asegura que hay 4 likes en la lista

def test_list_likes_of_post_no_access(createUsers,post_prueba_with_likes_and_comments):
    client,user1,user2,user3,_ = createUsers

    client.force_authenticate(user=user1)

    postdata_modified = {
        "title": "chao",
        "content": "chao",
        "public_access": "None",
        "authenticated_access": "None",
        "group_access": "None",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_with_likes_and_comments.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_200_OK

    response = client.get(reverse("blogpost-list-likes",kwargs={"pk": post_prueba_with_likes_and_comments.id}))
    assert response.status_code == status.HTTP_200_OK

    client.force_authenticate(user=None)

    response = client.get(reverse("blogpost-list-likes",kwargs={"pk": post_prueba_with_likes_and_comments.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND

    client.force_authenticate(user=user2)

    response = client.get(reverse("blogpost-list-likes",kwargs={"pk": post_prueba_with_likes_and_comments.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    client.force_authenticate(user=user3)

    response = client.get(reverse("blogpost-list-likes",kwargs={"pk": post_prueba_with_likes_and_comments.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND 

def test_get_like_can_access(createUsers, post_prueba_with_likes_and_comments):
    client, user1, user2, user3, _ = createUsers

    # 🔹 Obtener algunos likes
    like_user1 = Like.objects.get(post=post_prueba_with_likes_and_comments, user=user1)
    like_user3 = Like.objects.get(post=post_prueba_with_likes_and_comments, user=user3)

    # 🔹 Usuario no autenticado intenta ver un like (debería fallar con 403)
    client.force_authenticate(user=None)
    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_200_OK

    # 🔹 User1 intenta ver su propio like y el de user3 (debería permitirlo)
    client.force_authenticate(user=user1)
    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_200_OK

    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user3.id}))
    assert response.status_code == status.HTTP_200_OK

    # 🔹 User3 intenta ver su propio like y el de user1 (debería permitirlo)
    client.force_authenticate(user=user3)
    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user3.id}))
    assert response.status_code == status.HTTP_200_OK

    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_200_OK

    # 🔹 User2 intenta ver los likes de user1 y user3
    client.force_authenticate(user=user2)
    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_200_OK

    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user3.id}))
    assert response.status_code == status.HTTP_200_OK

def test_get_like_cannot_access(createUsers, post_prueba_with_likes_and_comments):
    client, user1, user2, user3, _ = createUsers

    client.force_authenticate(user=user1)

    postdata_modified = {
        "title": "chao",
        "content": "chao",
        "public_access": "None",
        "authenticated_access": "None",
        "group_access": "None",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_with_likes_and_comments.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_200_OK

    # 🔹 Obtener algunos likes
    like_user1 = Like.objects.get(post=post_prueba_with_likes_and_comments, user=user1)
    like_user3 = Like.objects.get(post=post_prueba_with_likes_and_comments, user=user3)

    # 🔹 Usuario no autenticado intenta ver un like (debería fallar con 401)
    client.force_authenticate(user=None)
    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # 🔹 User1 intenta ver su propio like y el de user3 (debería permitirlo)
    client.force_authenticate(user=user1)
    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_200_OK

    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user3.id}))
    assert response.status_code == status.HTTP_200_OK

    # 🔹 User3 intenta ver su propio like y el de user1 (debería permitirlo)
    client.force_authenticate(user=user3)
    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user3.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # 🔹 User2 intenta ver los likes de user1 y user3
    client.force_authenticate(user=user2)
    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.get(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user3.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_like_delete(createUsers, post_prueba_with_likes_and_comments):

    client, user1, user2, user3, _ = createUsers

    # 🔹 Obtener algunos likes
    like_user1 = Like.objects.get(post=post_prueba_with_likes_and_comments, user=user1)
    like_user3 = Like.objects.get(post=post_prueba_with_likes_and_comments, user=user3)

    # 🔹 Usuario no autenticado intenta ver un like (debería fallar con 403)
    client.force_authenticate(user=None)
    response = client.delete(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # 🔹 User2 intenta ver los likes de user1 y user3
    client.force_authenticate(user=user2)
    response = client.delete(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.delete(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user3.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # 🔹 User3 intenta ver su propio like y el de user1 (debería permitirlo)
    client.force_authenticate(user=user3)
    response = client.delete(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user3.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.delete(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

        # 🔹 User1 intenta ver su propio like y el de user3 (debería permitirlo)
    client.force_authenticate(user=user1)
    response = client.delete(reverse("blogpost-get-like", kwargs={"pk": post_prueba_with_likes_and_comments.id, "like_pk": like_user1.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_giving_like_as_staff_in_other_group(createUsers,post_prueba_only_author):
    
    client,_,user2,user3,user4 = createUsers
    client.force_authenticate(user=user3) #No está ni en el equipo

    # Ensure there are no likes before the request
    assert Like.objects.filter(post=post_prueba_only_author, user=user3).count() == 0

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_only_author.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Ensure the like was no created
    assert Like.objects.filter(post=post_prueba_only_author, user=user3).count() == 0

    client.force_authenticate(user=user2)  #No está ni en el equipo
    # Ensure there are no likes before the request
    assert Like.objects.filter(post=post_prueba_only_author, user=user2).count() == 0 

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_only_author.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Ensure the like was no created
    assert Like.objects.filter(post=post_prueba_only_author, user=user2).count() == 0

    # Entrando como staff
    client.force_authenticate(user=user4) #No está ni en el equipo

    # Ensure there are no likes before the request
    assert Like.objects.filter(post=post_prueba_only_author, user=user4).count() == 0

    response = client.post(reverse("blogpost-giving-like",kwargs={"pk": post_prueba_only_author.id}))
    assert response.status_code == status.HTTP_200_OK
    # Ensure the like was created
    assert Like.objects.filter(post=post_prueba_only_author, user=user4).count() == 1

#Testing comments on a post --------------------------------------------------------------------------------------------------------------------

def test_list_comment_post_with_access(createUsers, post_prueba_read_public_access):
    client,_,user2,user3,_ = createUsers

    client.force_authenticate(user=None)

    response = client.get(reverse("blogpost-list-comments", kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()  # 🔹 Convertimos la respuesta a JSON

    assert isinstance(response_data["results"], list) # 🔹 Verificamos que sea una lista
    assert len(response_data["results"]) == 0, f"Se esperaban 0 comentarios, pero se encontraron {len(response_data['results'])}"

    client.force_authenticate(user=user2)

    response = client.get(reverse("blogpost-list-comments", kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()  # 🔹 Convertimos la respuesta a JSON

    assert isinstance(response_data["results"], list), "La respuesta no es una lista de comentarios"  # 🔹 Verificamos que sea una lista
    assert len(response_data["results"]) == 0, f"Se esperaban 0 comentarios, pero se encontraron {len(response_data['results'])}"

    client.force_authenticate(user=user3)

    response = client.get(reverse("blogpost-list-comments", kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()  # 🔹 Convertimos la respuesta a JSON

    assert isinstance(response_data["results"], list), "La respuesta no es una lista de comentarios"  # 🔹 Verificamos que sea una lista
    assert len(response_data["results"]) == 0, f"Se esperaban 0 comentarios, pero se encontraron {len(response_data['results'])}"

def test_list_comment_post_with_no_access(createUsers, post_prueba_read_public_access):
    client,user1,user2,user3,_ = createUsers

    client.force_authenticate(user=user1)

    postdata_modified = {
        "title": "chao",
        "content": "chao",
        "public_access": "None",
        "authenticated_access": "None",
        "group_access": "None",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_read_public_access.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_200_OK

    client.force_authenticate(user=None)

    response = client.get(reverse("blogpost-list-comments", kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    client.force_authenticate(user=user2)

    response = client.get(reverse("blogpost-list-comments", kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    client.force_authenticate(user=user3)

    response = client.get(reverse("blogpost-list-comments", kwargs={"pk": post_prueba_read_public_access.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_list_comment_commenting_read_access(createUsers, post_prueba_read_only_access):

    client,user1,user2,user3,_ = createUsers

    data_comment = {"content": "Esto es un test"}
    #anonimo
    client.force_authenticate(user=None) 

    response = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_prueba_read_only_access.id}), data_comment)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    #autor
    client.force_authenticate(user=user1) 

    response = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_prueba_read_only_access.id}), data_comment)
    assert response.status_code == status.HTTP_201_CREATED
    #del team
    client.force_authenticate(user=user2)

    response = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_prueba_read_only_access.id}), data_comment)
    assert response.status_code == status.HTTP_201_CREATED

    #no es del team
    client.force_authenticate(user=user3)

    response = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_prueba_read_only_access.id}), data_comment)
    assert response.status_code == status.HTTP_201_CREATED

    # 🔹 Verificar que hay 3 comentarios en la BD (anónimo no pudo comentar)
    comment_count = Comment.objects.filter(post=post_prueba_read_only_access).count()
    assert comment_count == 3, f"Se esperaban 3 comentarios, pero se encontraron {comment_count}."

def test_list_comment_commenting_read_and_edit_access(createUsers, post_prueba_read_public_access):

    client,user1,user2,user3,_ = createUsers

    data_comment = {"content": "Esto es un test"}
    #anonimo
    client.force_authenticate(user=None) 

    response = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_prueba_read_public_access.id}), data_comment)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    #autor
    client.force_authenticate(user=user1) 

    response = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_prueba_read_public_access.id}), data_comment)
    assert response.status_code == status.HTTP_201_CREATED
    #del team
    client.force_authenticate(user=user2)

    response = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_prueba_read_public_access.id}), data_comment)
    assert response.status_code == status.HTTP_201_CREATED

    #no es del team
    client.force_authenticate(user=user3)

    response = client.post(reverse("blogpost-add-comment", kwargs={"pk": post_prueba_read_public_access.id}), data_comment)
    assert response.status_code == status.HTTP_201_CREATED

def test_get_comment_can_access(createUsers, post_prueba_with_likes_and_comments):

    client, user1, user2, user3, _ = createUsers

    # 🔹 Obtener algunos likes
    comment_user1 = Comment.objects.get(post=post_prueba_with_likes_and_comments, user=user1)
    comment_user3 = Comment.objects.get(post=post_prueba_with_likes_and_comments, user=user3)

    # 🔹 Usuario no autenticado intenta ver un like (debería fallar con 403)
    client.force_authenticate(user=None)
    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response.status_code == status.HTTP_200_OK

    # 🔹 User1 intenta ver su propio like y el de user3 (debería permitirlo)
    client.force_authenticate(user=user1)
    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response.status_code == status.HTTP_200_OK

    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}))
    assert response.status_code == status.HTTP_200_OK

    # 🔹 User3 intenta ver su propio like y el de user1 (debería permitirlo)
    client.force_authenticate(user=user3)
    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}))
    assert response.status_code == status.HTTP_200_OK

    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response.status_code == status.HTTP_200_OK

    # 🔹 User2 intenta ver los likes de user1 y user3
    client.force_authenticate(user=user2)
    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response.status_code == status.HTTP_200_OK

    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}))
    assert response.status_code == status.HTTP_200_OK

def test_get_comment_cannot_access(createUsers, post_prueba_with_likes_and_comments):

    client, user1, user2, user3, _ = createUsers

    client.force_authenticate(user=user1)

    postdata_modified = {
        "title": "chao",
        "content": "chao",
        "public_access": "None",
        "authenticated_access": "None",
        "group_access": "None",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_with_likes_and_comments.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_200_OK

    # 🔹 Obtener algunos likes
    comment_user1 = Comment.objects.get(post=post_prueba_with_likes_and_comments, user=user1)
    comment_user3 = Comment.objects.get(post=post_prueba_with_likes_and_comments, user=user3)

    # 🔹 Usuario no autenticado intenta ver un like (debería fallar con 403)
    client.force_authenticate(user=None)
    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # 🔹 User1 intenta ver su propio like y el de user3 (debería permitirlo)
    client.force_authenticate(user=user1)
    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response.status_code == status.HTTP_200_OK

    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}))
    assert response.status_code == status.HTTP_200_OK

    # 🔹 User3 intenta ver su propio like y el de user1 (debería permitirlo)
    client.force_authenticate(user=user3)
    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # 🔹 User2 intenta ver los likes de user1 y user3
    client.force_authenticate(user=user2)
    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.get(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_comment_permissions(createUsers, post_prueba_with_likes_and_comments):

    """
    Verifica que solo los autores de los comentarios puedan editarlos o eliminarlos.
    - Usuarios no autenticados no pueden modificar ni eliminar comentarios.
    - Otros usuarios autenticados no pueden modificar ni eliminar comentarios ajenos.
    - El autor del comentario sí puede modificarlo o eliminarlo.
    """

    client, user1, user2, user3, user4 = createUsers

    comment_data = {"content": "This should work"}

    # 🔹 Obtener comentarios creados por diferentes usuarios
    comment_user1 = Comment.objects.get(post=post_prueba_with_likes_and_comments, user=user1)
    comment_user3 = Comment.objects.get(post=post_prueba_with_likes_and_comments, user=user3)

    # 🛑 CASO 1: Usuario NO autenticado intenta modificar o eliminar comentarios (debería fallar con 403)
    client.force_authenticate(user=None)
    
    response_delete = client.delete(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response_delete.status_code == status.HTTP_403_FORBIDDEN, "Un usuario no autenticado no debería poder eliminar un comentario"
    
    response_put = client.put(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}), comment_data)
    assert response_put.status_code == status.HTTP_403_FORBIDDEN, "Un usuario no autenticado no debería poder editar un comentario"

    # 🛑 CASO 2: User2 intenta modificar o eliminar comentarios de User1 y User3 (debería fallar con 403)
    client.force_authenticate(user=user2)

    response_delete = client.delete(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response_delete.status_code == status.HTTP_403_FORBIDDEN, "User2 no debería poder eliminar un comentario de User1"

    response_put = client.put(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}), comment_data)
    assert response_put.status_code == status.HTTP_403_FORBIDDEN, "User2 no debería poder editar un comentario de User1"

    # 🛑 CASO 3: User4 intenta modificar/eliminar comentario de User3 (debería fallar con 403)
    client.force_authenticate(user=user4)

    response_delete = client.delete(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}))
    assert response_delete.status_code == status.HTTP_403_FORBIDDEN, "User4 no debería poder eliminar un comentario de User3"

    response_put = client.put(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}), comment_data)
    assert response_put.status_code == status.HTTP_403_FORBIDDEN, "User4 no debería poder editar un comentario de User3"

    response_patch = client.patch(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}), comment_data)
    assert response_patch.status_code == status.HTTP_403_FORBIDDEN, "User4 no debería poder modificar parcialmente un comentario de User3"

    # ✅ CASO 4: User3 intenta modificar/eliminar su propio comentario (debería poder hacerlo)
    client.force_authenticate(user=user3)

    response_put = client.put(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}), comment_data)
    assert response_put.status_code == status.HTTP_200_OK, "User3 debería poder editar su propio comentario"

    response_patch = client.patch(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}), comment_data)
    assert response_patch.status_code == status.HTTP_200_OK, "User3 debería poder modificar parcialmente su comentario"

    response_delete = client.delete(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user3.id}))
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT, "User3 debería poder eliminar su propio comentario"

    # 🛑 CASO 5: User3 intenta modificar/eliminar comentario de User1 (debería fallar con 403)
    response_delete = client.delete(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response_delete.status_code == status.HTTP_403_FORBIDDEN, "User3 no debería poder eliminar un comentario de User1"

    response_put = client.put(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}), comment_data)
    assert response_put.status_code == status.HTTP_403_FORBIDDEN, "User3 no debería poder editar un comentario de User1"

    # ✅ CASO 6: User1 intenta modificar/eliminar su propio comentario (debería poder hacerlo)
    client.force_authenticate(user=user1)

    response_put = client.put(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}), comment_data)
    assert response_put.status_code == status.HTTP_200_OK, "User1 debería poder editar su propio comentario"

    response_patch = client.patch(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}), comment_data)
    assert response_patch.status_code == status.HTTP_200_OK, "User1 debería poder modificar parcialmente su comentario"

    response_delete = client.delete(reverse("blogpost-get-comment", kwargs={"pk": post_prueba_with_likes_and_comments.id, "comment_pk": comment_user1.id}))
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT, "User1 debería poder eliminar su propio comentario"

#Testing likes on a post http://127.0.0.1:8000/api/likes/` --------------------------------------------------------------------------------------------------------------------

def test_filter_likes_by_post_and_user(post_prueba_with_likes_and_comments, createUsers):
    client, user1, user2, user3, _ = createUsers
    post = post_prueba_with_likes_and_comments

    # Autenticar como el autor
    client.force_authenticate(user=user1)

    url = reverse('likes-list')
    response = client.get(url, {
        'post_id': post.id,
        'user_id': user1.id,
        'page': 1
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 1

    result = response.data["results"][0]
    assert result["user"] == user1.username
    assert result["post_id"] == post.id

    # Autenticar como el alguien diferente al autor
    client.force_authenticate(user=user2)

    url = reverse('likes-list')
    response = client.get(url, {
        'post_id': post.id,
        'user_id': user1.id,
        'page': 1
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 1

    result = response.data["results"][0]
    assert result["user"] == user1.username
    assert result["post_id"] == post.id

    # Autenticar como el usuario en grupo diferente
    client.force_authenticate(user=user3)
    response = client.get(url, {
        'post_id': post.id,
        'user_id': user1.id,
        'page': 1
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 1

    result = response.data["results"][0]
    assert result["user"] == user1.username
    assert result["post_id"] == post.id

    # Autenticar como un no autenticado
    client.force_authenticate(user=None)
    response = client.get(url, {
        'post_id': post.id,
        'user_id': user1.id,
        'page': 1
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 1

    result = response.data["results"][0]
    assert result["user"] == user1.username
    assert result["post_id"] == post.id

def test_likes_pagination(post_prueba_with_likes_and_comments, createUsers):
    client, user1, _, _, _ = createUsers
    post = post_prueba_with_likes_and_comments

    client.force_authenticate(user=user1)

    url = reverse('likes-list')

    # Pide la primera página
    response_page_1 = client.get(url, {
        'post_id': post.id,
        'page': 1
    })
    assert response_page_1.status_code == status.HTTP_200_OK
    assert response_page_1.data["total_count"] == 4  # hay 4 likes en total
    assert len(response_page_1.data["results"]) == 1
    assert "next" in response_page_1.data
    assert response_page_1.data["next"] is not None

    # Pide la segunda página
    response_page_2 = client.get(url, {
        'post_id': post.id,
        'page': 2
    })
    assert response_page_2.status_code == status.HTTP_200_OK
    assert len(response_page_2.data["results"]) == 1
    assert response_page_2.data["next"] is not None

    # Pide la última página
    response_page_4 = client.get(url, {
        'post_id': post.id,
        'page': 4
    })
    assert response_page_4.status_code == status.HTTP_200_OK
    assert len(response_page_4.data["results"]) == 1
    assert response_page_4.data["next"] is None  # no hay más páginas

    # Pide una página inexistente
    response_page_5 = client.get(url, {
        'post_id': post.id,
        'page': 5
    })
    assert response_page_5.status_code == status.HTTP_404_NOT_FOUND

def test_user_cannot_view_private_post_likes(post_prueba_with_likes_and_comments_privado, createUsers):
    client, user1, user2, user3, _ = createUsers
    post = post_prueba_with_likes_and_comments_privado

    # Autenticar como un usuario no autorizado (user2)
    client.force_authenticate(user=user2)

    url = reverse('likes-list')
    response = client.get(url, {
        'post_id': post.id,
        'page': 1
    })

    # devuelve 200 pero sin resultados visibles
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 0

    # Autenticar como un usuario no autorizado (user3)
    client.force_authenticate(user=user3)

    url = reverse('likes-list')
    response = client.get(url, {
        'post_id': post.id,
        'page': 1
    })

    # devuelve 200 pero sin resultados visibles
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 0

    # Autenticar como un usuario autorizado (user1)
    client.force_authenticate(user=user1)

    url = reverse('likes-list')
    response = client.get(url, {
        'post_id': post.id,
        'page': 1
    })

    # devuelve 200 pero sin resultados visibles
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 1

def test_user_cannot_view_private_post_likes_group_access(post_prueba_with_likes_and_comments_group_access, createUsers):
    client, user1, user2, user3, _ = createUsers
    post = post_prueba_with_likes_and_comments_group_access

    client.force_authenticate(user=user1)

    url = reverse('likes-list')
    response = client.get(url, {
        'post_id': post.id,
        'page': 1
    })

    # devuelve 200 pero sin resultados visibles
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 1

    # Autenticar como un usuario no autorizado (user3)
    client.force_authenticate(user=user3)

    url = reverse('likes-list')
    response = client.get(url, {
        'post_id': post.id,
        'page': 1
    })

    # devuelve 200 pero sin resultados visibles
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 0

    # Autenticar como un usuario autorizado (user1)
    client.force_authenticate(user=user2)

    url = reverse('likes-list')

    response_like = client.post(reverse("blogpost-giving-like", kwargs={"pk": post.id}))
    assert response_like.status_code == 200  # ✅ Asegurar que la petición fue exitosa

    response = client.get(url, {
        'post_id': post.id,
        'page': 1
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 2

        # Autenticar como un usuario no autenticado
    client.force_authenticate(user=None)

    url = reverse('likes-list')

    response = client.get(url, {
        'post_id': post.id,
        'page': 1
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 0

def test_user_cannot_view_private_post_likes_authenticated_access(post_prueba_with_likes_and_comments_authenticated_access, createUsers):
    client, user1, user2, user3, _ = createUsers
    post = post_prueba_with_likes_and_comments_authenticated_access

    client.force_authenticate(user=user1)

    url = reverse('likes-list')
    response = client.get(url, {
        'post_id': post.id,
        'page': 1
    })

    # devuelve 200 pero sin resultados visibles
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 1

    client.force_authenticate(user=user3)

    url = reverse('likes-list')
    response = client.get(url, {
        'post_id': post.id,
        'page': 1
    })

    # devuelve 200 pero sin resultados visibles
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 1

    client.force_authenticate(user=user2)

    url = reverse('likes-list')

    response_like = client.post(reverse("blogpost-giving-like", kwargs={"pk": post.id}))
    assert response_like.status_code == 200  # ✅ Asegurar que la petición fue exitosa

    response = client.get(url, {
        'post_id': post.id,
        'page': 1
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 2

    # Autenticar como un usuario no autenticado
    client.force_authenticate(user=None)

    url = reverse('likes-list')

    response = client.get(url, {
        'post_id': post.id,
        'page': 1
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_count"] == 0


    

