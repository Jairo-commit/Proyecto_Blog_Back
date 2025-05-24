import pytest
import json
from django.urls import reverse
from rest_framework import status

from test_setup_posts import createUsers, post_prueba, post_prueba_read_public_access, post_prueba_read_authenticated_access, post_prueba_none_authenticated_access, post_prueba_read_group_access, post_prueba_only_author
from posts.models import BlogPost

#Create post -------------------------------------------------------------------------------------------------------------------------
def test_create_post(createUsers):
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

    response_get = client.get(reverse("blogpost-list"))
    assert response_get.status_code == status.HTTP_200_OK, f"Error: {response_get.data}"

    # Realizar una solicitud POST al endpoint
    response_post = client.post(reverse("blogpost-list"), json.dumps(postdata), content_type="application/json")

   # Verificar que la respuesta sea 201 CREATED
    assert response_post.status_code == status.HTTP_201_CREATED, f"Error: {response_post.data}"

    # Verificar que el post realmente se creó en la base de datos
    assert BlogPost.objects.filter(title="Post de prueba para loggueados").exists(), "El post no se creó correctamente"

#Test GET, POST, PATCH and DELETE author----------------------------------------------------------------------------------------------------

def test_author_access(createUsers,post_prueba_only_author):
    client,user1,_,_,_ = createUsers
    client.force_authenticate(user=user1) #user1 is the post_prueba_only_author's author 
    response = client.get(reverse("blogpost-detail", args=[post_prueba_only_author.id])) 
    assert response.status_code == status.HTTP_200_OK

    postdata_modified = {
        "title": "Post de prueba para loggueados Edit: user1",
        "content": "You gotta be logged in",
        "public_access": "Read",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_only_author.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_200_OK

    postdata_modified2 = {
        "content": "You gotta be logged in edit: user1",
    }
    response_patch = client.patch(reverse("blogpost-detail", args=[post_prueba_only_author.id]), json.dumps(postdata_modified2), content_type="application/json") 
    assert response_patch.status_code == status.HTTP_200_OK
    
    assert BlogPost.objects.filter(title="Post de prueba para loggueados Edit: user1").exists()
    assert BlogPost.objects.filter(content="You gotta be logged in edit: user1").exists()
    assert BlogPost.objects.filter(public_access="Read").exists()

    response_delete = client.delete(reverse("blogpost-detail", args=[post_prueba_only_author.id])) 
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT

#Test POST unauthenticated ----------------------------------------------------------------------------------------------------

def test_POST_unauthenticated(createUsers):
    client,_,_,_,_ = createUsers

    client.force_authenticate(user=None)

    # Datos del nuevo post
    postdata = {
        "title": "Post de prueba para el grupo",
        "content": "This post can be edit for the team, but It can't be read by authenticated people",
        "public_access": "None",
        "authenticated_access": "None",
        "group_access": "None",
        "author_access": "Read and Edit",
    }

    response = client.post(reverse("blogpost-list"), json.dumps(postdata), content_type="application/json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST

#Test GET, POST, PATCH and DELETE unauthenticated "public_access": "None",----------------------------------------------------------------------------------------------------

def test_unauthenticated_user_none(createUsers,post_prueba):

    client,_,_,_,_ = createUsers
    client.force_authenticate(user=None)

    response = client.get(reverse("blogpost-detail", args=[post_prueba.id])) 
    assert response.status_code == status.HTTP_404_NOT_FOUND

    postdata_modified = {
        "title": "Post de prueba para loggueados Edit: user1",
        "content": "You gotta be logged in",
        "public_access": "Read",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }

    response_put = client.put(reverse("blogpost-detail", args=[post_prueba.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_404_NOT_FOUND

    postdata_modified2 = {
        "content": "You gotta be logged in edit: user1",
    }
    response_patch = client.patch(reverse("blogpost-detail", args=[post_prueba.id]), json.dumps(postdata_modified2), content_type="application/json") 
    assert response_patch.status_code == status.HTTP_404_NOT_FOUND
    
    response_delete = client.delete(reverse("blogpost-detail", args=[post_prueba.id])) 
    assert response_delete.status_code == status.HTTP_404_NOT_FOUND

#Test GET, POST, PATCH and DELETE unauthenticated "public_access": "Read",----------------------------------------------------------------------------------------------------

def test_unauthenticated_user_read(createUsers,post_prueba_read_public_access):

    client,_,_,_,_ = createUsers
    client.force_authenticate(user=None)

    response = client.get(reverse("blogpost-detail", args=[post_prueba_read_public_access.id])) 
    assert response.status_code == status.HTTP_200_OK

    postdata_modified = {
        "title": "Post de prueba para loggueados Edit: user1",
        "content": "You gotta be logged in",
        "public_access": "Read",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }

    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_read_public_access.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_401_UNAUTHORIZED
    postdata_modified2 = {
        "content": "You gotta be logged in edit: user1",
    }
    response_patch = client.patch(reverse("blogpost-detail", args=[post_prueba_read_public_access.id]), json.dumps(postdata_modified2), content_type="application/json") 
    assert response_patch.status_code == status.HTTP_401_UNAUTHORIZED
    
    response_delete = client.delete(reverse("blogpost-detail", args=[post_prueba_read_public_access.id])) 
    assert response_delete.status_code == status.HTTP_401_UNAUTHORIZED

#Test GET, POST, PATCH and DELETE "authenticated_access": "Read and Edit",----------------------------------------------------------------------------------------------------

def test_authenticated_user_read_and_edit(createUsers,post_prueba): #user 3 solo puede editar el post por su permiso de autenticado
    client,_,_,user3,_ = createUsers
    client.force_authenticate(user=user3) #user1 is the post_prueba's author 
    response = client.get(reverse("blogpost-detail", args=[post_prueba.id])) 
    assert response.status_code == status.HTTP_200_OK

    postdata_modified = {
        "title": "Post de prueba para loggueados Edit: user3",
        "content": "You gotta be logged in",
        "public_access": "Read",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_200_OK

    postdata_modified2 = {
        "content": "You gotta be logged in edit: user3",
    }
    response_patch = client.patch(reverse("blogpost-detail", args=[post_prueba.id]), json.dumps(postdata_modified2), content_type="application/json") 
    assert response_patch.status_code == status.HTTP_200_OK
    
    assert BlogPost.objects.filter(title="Post de prueba para loggueados Edit: user3").exists()
    assert BlogPost.objects.filter(content="You gotta be logged in edit: user3").exists()
    assert BlogPost.objects.filter(public_access="Read").exists()

    response_delete = client.delete(reverse("blogpost-detail", args=[post_prueba.id])) 
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT

#Test GET, POST, PATCH and DELETE "authenticated_access": "Read"----------------------------------------------------------------------------------------------------

#user 3 solo puede leer el post por su permiso de autenticado 
#No puede modificarlo

def test_authenticated_user_read(createUsers,post_prueba_read_authenticated_access): 
    client,_,_,user3,_ = createUsers                                                
    client.force_authenticate(user=user3) #user1 is the post_prueba's author 
    response = client.get(reverse("blogpost-detail", args=[post_prueba_read_authenticated_access.id])) 
    assert response.status_code == status.HTTP_200_OK

    postdata_modified = {
        "title": "Post de prueba para loggueados Edit: user3",
        "content": "You gotta be logged in",
        "public_access": "Read",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_read_authenticated_access.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_403_FORBIDDEN

    postdata_modified2 = {
        "content": "You gotta be logged in edit: user3",
    }
    response_patch = client.patch(reverse("blogpost-detail", args=[post_prueba_read_authenticated_access.id]), json.dumps(postdata_modified2), content_type="application/json") 
    assert response_patch.status_code == status.HTTP_403_FORBIDDEN
    
    assert BlogPost.objects.filter(title="Post de prueba para loggueados solo lectura").exists()
    assert BlogPost.objects.filter(content="This post can be read by people who is loggued").exists()
    assert BlogPost.objects.filter(public_access="None").exists()

    response_delete = client.delete(reverse("blogpost-detail", args=[post_prueba_read_authenticated_access.id])) 
    assert response_delete.status_code == status.HTTP_403_FORBIDDEN

#Test GET, POST, PATCH and DELETE "authenticated_access": "None"----------------------------------------------------------------------------------------------------

#user 3 no puede ni leer el post por su permiso de autenticado 
#No puede modificarlo

def test_authenticated_user_none(createUsers,post_prueba_none_authenticated_access): 
    client,_,_,user3,_ = createUsers                                                
    client.force_authenticate(user=user3) #user1 is the post_prueba's author 
    response = client.get(reverse("blogpost-detail", args=[post_prueba_none_authenticated_access.id])) 
    assert response.status_code == status.HTTP_404_NOT_FOUND

    postdata_modified = {
        "title": "Post de prueba para loggueados Edit: user3",
        "content": "You gotta be logged in",
        "public_access": "Read",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_none_authenticated_access.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_404_NOT_FOUND

    postdata_modified2 = {
        "content": "You gotta be logged in edit: user3",
    }
    response_patch = client.patch(reverse("blogpost-detail", args=[post_prueba_none_authenticated_access.id]), json.dumps(postdata_modified2), content_type="application/json") 
    assert response_patch.status_code == status.HTTP_404_NOT_FOUND
    
    response_delete = client.delete(reverse("blogpost-detail", args=[post_prueba_none_authenticated_access.id])) 
    assert response_delete.status_code == status.HTTP_404_NOT_FOUND

#Test GET, POST, PATCH and DELETE unauthenticated "group_access": "Read and Edit"----------------------------------------------------------------------------------------------------

#user 3 no puede ni leer el post por su permiso de autenticado 
#No puede modificarlo
# El usuario 2 sí debería hacerlo porque pertenece al grupo

def test_team_user_read_and_edit(createUsers,post_prueba_none_authenticated_access): 
    
    client,_,user2,_,_ = createUsers                                                
    client.force_authenticate(user=user2) #user1 is the post_prueba's author 
    response = client.get(reverse("blogpost-detail", args=[post_prueba_none_authenticated_access.id])) 
    assert response.status_code == status.HTTP_200_OK

    postdata_modified = {
        "title": "Post de prueba para loggueados Edit: user3",
        "content": "You gotta be logged in",
        "public_access": "Read",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_none_authenticated_access.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_200_OK

    postdata_modified2 = {
        "content": "You gotta be logged in edit: user3",
    }
    response_patch = client.patch(reverse("blogpost-detail", args=[post_prueba_none_authenticated_access.id]), json.dumps(postdata_modified2), content_type="application/json") 
    assert response_patch.status_code == status.HTTP_200_OK
    
    response_delete = client.delete(reverse("blogpost-detail", args=[post_prueba_none_authenticated_access.id])) 
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT

#Test GET, POST, PATCH and DELETE unauthenticated "group_access": "Read"----------------------------------------------------------------------------------------------------

#user 2 solo puede leer el post por su permiso de grupo 

def test_team_user_read(createUsers,post_prueba_read_group_access): 
    
    client,_,user2,_,_ = createUsers                                                
    client.force_authenticate(user=user2) #user1 is the post_prueba's author 
    response = client.get(reverse("blogpost-detail", args=[post_prueba_read_group_access.id])) 
    assert response.status_code == status.HTTP_200_OK

    postdata_modified = {
        "title": "Post de prueba para loggueados Edit: user3",
        "content": "You gotta be logged in",
        "public_access": "Read",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_read_group_access.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_403_FORBIDDEN

    postdata_modified2 = {
        "content": "You gotta be logged in edit: user3",
    }
    response_patch = client.patch(reverse("blogpost-detail", args=[post_prueba_read_group_access.id]), json.dumps(postdata_modified2), content_type="application/json") 
    assert response_patch.status_code == status.HTTP_403_FORBIDDEN
    
    response_delete = client.delete(reverse("blogpost-detail", args=[post_prueba_read_group_access.id])) 
    assert response_delete.status_code == status.HTTP_403_FORBIDDEN

#Test GET, POST, PATCH and DELETE unauthenticated "group_access": "None"----------------------------------------------------------------------------------------------------

#user 2 solo puede leer el post por su permiso de grupo 

def test_team_user_none(createUsers,post_prueba_only_author): 
    
    client,_,user2,_,_ = createUsers                                                
    client.force_authenticate(user=user2) #user1 is the post_prueba's author 
    response = client.get(reverse("blogpost-detail", args=[post_prueba_only_author.id])) 
    assert response.status_code == status.HTTP_404_NOT_FOUND

    postdata_modified = {
        "title": "Post de prueba para loggueados Edit: user3",
        "content": "You gotta be logged in",
        "public_access": "Read",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_only_author.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_404_NOT_FOUND

    postdata_modified2 = {
        "content": "You gotta be logged in edit: user3",
    }
    response_patch = client.patch(reverse("blogpost-detail", args=[post_prueba_only_author.id]), json.dumps(postdata_modified2), content_type="application/json") 
    assert response_patch.status_code == status.HTTP_404_NOT_FOUND
    
    response_delete = client.delete(reverse("blogpost-detail", args=[post_prueba_only_author.id])) 
    assert response_delete.status_code == status.HTTP_404_NOT_FOUND


    
    client,user1,_,_,_ = createUsers                                                
    client.force_authenticate(user=user1) #user1 is the post_prueba's author 
    response = client.get(reverse("blogpost-detail", args=[post_prueba_only_author.id])) 
    assert response.status_code == status.HTTP_200_OK

    postdata_modified = {
        "title": "Post de prueba para loggueados Edit: user3",
        "content": "You gotta be logged in",
        "public_access": "Read",
        "authenticated_access": "Read and Edit",
        "group_access": "Read and Edit",
        "author_access": "Read and Edit",
    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_only_author.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_200_OK

    postdata_modified2 = {
        "content": "You gotta be logged in edit: user3",
    }
    response_patch = client.patch(reverse("blogpost-detail", args=[post_prueba_only_author.id]), json.dumps(postdata_modified2), content_type="application/json") 
    assert response_patch.status_code == status.HTTP_200_OK
    
    response_delete = client.delete(reverse("blogpost-detail", args=[post_prueba_only_author.id])) 
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT

# PUT incomplete information --------------------------------------------------------------------------------------------------------------------

def test_put_bad_request(createUsers,post_prueba_only_author):
    client,user1,_,_,_ = createUsers
    client.force_authenticate(user=user1) #user1 is the post_prueba_only_author's author 
    response = client.get(reverse("blogpost-detail", args=[post_prueba_only_author.id])) 
    assert response.status_code == status.HTTP_200_OK

    postdata_modified = {
        "title": "Post de prueba para loggueados Edit: user1",
        "content": "You gotta be logged in",

    }
    response_put = client.put(reverse("blogpost-detail", args=[post_prueba_only_author.id]), json.dumps(postdata_modified), content_type="application/json") 
    assert response_put.status_code == status.HTTP_400_BAD_REQUEST