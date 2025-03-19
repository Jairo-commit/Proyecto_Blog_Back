from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User, Group


from .models import BlogPost

# Create your tests here.

class PostTestCase(TestCase): #Here, I'm testing unauthenticated permissions as well

    def setUp(self):

        self.user_data = {
            'username': 'prueba', 
            'password': 'prueba123',
            'first_name': 'nombre',
            'last_name': 'apellido',
            'email': 'example@example.com'
        }
        self.client.post(reverse('user_register-list'), self.user_data)
        self.user = User.objects.get(username = self.user_data['username'])

        self.client.login(username='prueba', password='prueba123')  

        postdata = {
            'title': 'Post de prueba para loggueados',
            'content': 'You gotta be logged in',
            'public_access': 'None',
            'authenticated_access': "Read and Edit",
            'group_access': "Read and Edit",
            'author_access': "Read and Edit",
        }
         # Crear el post autenticado
        self.client.post(reverse('blogpost-list'), postdata, content_type='application/json')

        self.post_de_prueba = BlogPost.objects.get(title = "Post de prueba para loggueados")

        self.client.logout()

# Test relacionados para el usuario que no está logueado

    def test_unauthenticated_create_blog_post(self):
        
        data = {
            'title': 'Unauthorized Post',
            'content': 'Should not be created.',
            'public_access': 'Read',
            'authenticated_access': "Read and Edit",
            'group_access': "Read and Edit",
            'author_access': "Read and Edit",
        }
        response = self.client.post(reverse('blogpost-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_list_access(self):
        response = self.client.get(reverse('blogpost-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_read_access(self):
        self.client.login(username='prueba', password='prueba123')

        updated_data = {
        'public_access': 'Read',
        }
        response_actualizado = self.client.patch(reverse('blogpost-detail', 
                                                       args=[self.post_de_prueba.id]), updated_data, 
                                                       content_type="application/json")
        
        self.client.logout()
        response = self.client.get(reverse('blogpost-detail', args=[self.post_de_prueba.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_unauthenticated_none_access(self):
        response = self.client.get(reverse('blogpost-detail', args=[self.post_de_prueba.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_blog_post(self):
        # Hacer login de forma directa en los tests
        login_successful = self.client.post(reverse('rest_framework:login'), self.user_data)
        self.assertEqual(login_successful.status_code, status.HTTP_302_FOUND) 

        # Datos del post a crear
        data = {
            'title': 'My Test Post',
            'content': 'This is a test blog post.',
            'public_access': 'Read',
            'authenticated_access': "Read and Edit",
            'group_access': "Read and Edit",
            'author_access': "Read and Edit",
        }

        response = self.client.post(reverse('blogpost-list'), data)

        post_created = BlogPost.objects.get(title='My Test Post')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Fallo en la creación del post")
        self.assertEqual(post_created.title, 'My Test Post')
        self.assertEqual(post_created.author.username, 'prueba')
        self.assertEqual(post_created.content, 'This is a test blog post.')
        self.assertEqual(post_created.excerpt, 'This is a test blog post.')
        self.assertIsNotNone(post_created.pk) 
        self.assertEqual(post_created.public_access, 'Read')
        self.assertEqual(post_created.authenticated_access, 'Read and Edit')
        self.assertEqual(post_created.group_access, 'Read and Edit')
        self.assertEqual(post_created.author_access, 'Read and Edit')


    def test_update_blog_post_same_user(self):
        """Verifica que un usuario autenticado pueda actualizar su propio post."""
        self.client.login(username='prueba', password='prueba123')

        # Datos del post a crear
        data = {
            'title': 'My Test Post',
            'content': 'This is a test blog post.',
            'public_access': 'Read',
            'authenticated_access': "Read and Edit",
            'group_access': "Read and Edit",
            'author_access': "Read and Edit",
        }
        response_original = self.client.post(reverse('blogpost-list'), data)

        updated_data = {
        'title': 'Updated Title',
        'content': 'Updated Content',
        'public_access': 'None',
        'authenticated_access': "Read and Edit",
        'group_access': "Read and Edit",
        'author_access': "Read and Edit",
        }
        response_actualizado = self.client.put(reverse('blogpost-detail', args=[response_original.data['id']]), updated_data, content_type="application/json")

        self.assertEqual(response_actualizado.status_code, status.HTTP_200_OK, "Error al actualizar el post")


class PostTestCase_authenticated_access(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'prueba', 
            'password': 'prueba123',
            'first_name': 'nombre',
            'last_name': 'apellido',
            'email': 'example@example.com'
        }
        self.client.post(reverse('user_register-list'), self.user_data)
        self.user = User.objects.get(username = self.user_data['username'])

        self.user_data2 = {
            'username': 'prueba2', 
            'password': 'prueba1234',
            'first_name': 'nombre2',
            'last_name': 'apellido2',
            'email': 'example2@example.com'
        }

        self.client.post(reverse('user_register-list'), self.user_data2)
        self.user2 = User.objects.get(username = self.user_data2['username'])

        self.user_data3 = { #Usuario en equipo diferente
            'username': 'prueba3', 
            'password': 'prueba12345',
            'first_name': 'nombre3',
            'last_name': 'apellido3',
            'email': 'example3@example.com'
        }

        self.client.post(reverse('user_register-list'), self.user_data3)
        self.user3 = User.objects.get(username = self.user_data3['username'])

        # Create a different group for user3
        different_group, created = Group.objects.get_or_create(name="Different Group")
        self.user3.groups.remove(Group.objects.get(name ='default_team'))
        self.user3.groups.add(different_group)  # Assign to Different Group

        self.client.login(username='prueba', password='prueba123')  

        postdata = {
            'title': 'Post de prueba para loggueados',
            'content': 'You gotta be logged in',
            'public_access': 'None',
            'authenticated_access': "Read and Edit",
            'group_access': "Read and Edit",
            'author_access': "Read and Edit",
        }
         # Crear el post autenticado
        self.client.post(reverse('blogpost-list'), postdata, content_type='application/json')
        self.post_de_prueba = BlogPost.objects.get(title = "Post de prueba para loggueados")

        postdata_soloread = {
            'title': 'Post de prueba que solo se lee',
            'content': 'Only the author can edit this post',
            'public_access': 'None',
            'authenticated_access': "Read",
            'group_access': "Read",
            'author_access': "Read and Edit",
        }
        self.client.post(reverse('blogpost-list'), postdata_soloread, content_type='application/json')

        self.postdata_soloread = BlogPost.objects.get(title = "Post de prueba que solo se lee")

        postdata_soloteam = {
            'title': 'Post de prueba que solo puede leer el group',
            'content': 'Only the group can read, but not edit, this post',
            'public_access': 'None',
            'authenticated_access': "None",
            'group_access': "Read",
            'author_access': "Read and Edit",
        }
        self.client.post(reverse('blogpost-list'), postdata_soloteam, content_type='application/json')

        self.postdata_soloteam = BlogPost.objects.get(title = "Post de prueba que solo puede leer el group")

        self.client.logout()

    def test_read_and_edit_permissions(self):

        self.client.login(username='prueba2', password='prueba1234')
        
        response_get =self.client.get(reverse('blogpost-list'))
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)

        response_get2 =self.client.get(reverse('blogpost-detail', args=[self.post_de_prueba.id]))
        self.assertEqual(response_get2.status_code, status.HTTP_200_OK)

        postdata = {
            'title': 'Post de prueba para loggueados',
            'content': 'You gotta be logged in edit: prueba2', #modified
            'public_access': 'None',
            'authenticated_access': "Read and Edit",
            'group_access': "Read and Edit",
            'author_access': "Read and Edit",
        }
        response_put = self.client.put(reverse('blogpost-detail', args=[self.post_de_prueba.id]), 
                                       postdata, content_type="application/json")
        self.assertEqual(response_put.status_code, status.HTTP_200_OK)
        postdata = {
            'title': 'Post de prueba para loggueados Edit: prueba 2 patch', #modified
            'public_access': 'Read', #modified
        }
        response_patch = self.client.patch(reverse('blogpost-detail', args=[self.post_de_prueba.id]), 
                                       postdata, content_type="application/json")
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK, "Error al actualizar el post")
        response_delete = self.client.delete(reverse('blogpost-detail', args=[self.post_de_prueba.id]))
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT, "Error al borrar el post")

        response_get =self.client.get('blogpost-detail', args=[self.post_de_prueba.id])
        self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND) #hacer esta prueba luego, creo que se debería ubicar mejor

    def test_read_permissions(self):
        self.client.login(username='prueba2', password='prueba1234')

        response_get2 =self.client.get(reverse('blogpost-detail', args=[self.postdata_soloread.id]))
        self.assertEqual(response_get2.status_code, status.HTTP_200_OK)

        postdata_soloread = {
            'title': 'Post de prueba que solo se lee',
            'content': 'Only the author can edit this post',
            'public_access': 'None',
            'authenticated_access': "Read",
            'group_access': "Read",
            'author_access': "Read and Edit",
        }
        response_put = self.client.put(reverse('blogpost-detail', args=[self.postdata_soloread.id]), 
                                       postdata_soloread, content_type="application/json")
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)
        postdata_soloread = {
            'title': 'Post de prueba que solo se lee Edit: prueba 2 patch', #modified
            'public_access': 'Read', #modified
        }
        response_patch = self.client.patch(reverse('blogpost-detail', args=[self.postdata_soloread.id]), 
                                       postdata_soloread, content_type="application/json")
        self.assertEqual(response_patch.status_code, status.HTTP_403_FORBIDDEN, "Error al actualizar el post")
        response_delete = self.client.delete(reverse('blogpost-detail', args=[self.postdata_soloread.id]))
        self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN, "Error al borrar el post")

    def test_none_permissions(self):
        self.client.login(username='prueba3', password='prueba12345')

        response_get2 =self.client.get(reverse('blogpost-detail', args=[self.postdata_soloteam.id]))
        self.assertEqual(response_get2.status_code, status.HTTP_404_NOT_FOUND)

        postdata_soloteam = {
            'title': 'Post de prueba que solo puede leer el group',
            'content': 'Only the group can read, but not edit, this post',
            'public_access': 'None',
            'authenticated_access': "None",
            'group_access': "Read",
            'author_access': "Read and Edit",
        }
        response_put = self.client.put(reverse('blogpost-detail', args=[self.postdata_soloteam.id]), 
                                       postdata_soloteam, content_type="application/json")
        self.assertEqual(response_put.status_code, status.HTTP_404_NOT_FOUND)
        postdata_soloteam = {
            'title': 'Post de prueba que solo puede leer el group Edit: prueba 2 patch', #modified
            'public_access': 'Read', #modified
        }
        response_patch = self.client.patch(reverse('blogpost-detail', args=[self.postdata_soloteam.id]), 
                                       postdata_soloteam, content_type="application/json")
        self.assertEqual(response_patch.status_code, status.HTTP_404_NOT_FOUND, "Error al actualizar el post")
        response_delete = self.client.delete(reverse('blogpost-detail', args=[self.postdata_soloteam.id]))
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND, "Error al borrar el post")
    
# class PostTestCase_group_access(TestCase):
#     def setUp(self):
#         self.user_data = {
#             'username': 'prueba', 
#             'password': 'prueba123',
#             'first_name': 'nombre',
#             'last_name': 'apellido',
#             'email': 'example@example.com'
#         }
#         self.client.post(reverse('user_register-list'), self.user_data)
#         self.user = User.objects.get(username = self.user_data['username'])

#         self.user_data2 = {
#             'username': 'prueba2', 
#             'password': 'prueba1234',
#             'first_name': 'nombre2',
#             'last_name': 'apellido2',
#             'email': 'example2@example.com'
#         }

#         self.client.post(reverse('user_register-list'), self.user_data2)
#         self.user2 = User.objects.get(username = self.user_data2['username'])

#         self.user_data3 = { #Usuario en equipo diferente
#             'username': 'prueba3', 
#             'password': 'prueba12345',
#             'first_name': 'nombre3',
#             'last_name': 'apellido3',
#             'email': 'example3@example.com'
#         }

#         self.client.post(reverse('user_register-list'), self.user_data3)
#         self.user3 = User.objects.get(username = self.user_data3['username'])

#         # Create a different group for user3
#         different_group, created = Group.objects.get_or_create(name="Different Group")
#         self.user3.groups.remove(Group.objects.get(name ='default_team'))
#         self.user3.groups.add(different_group)  # Assign to Different Group

#         self.client.login(username='prueba', password='prueba123')  

#         postdata = {
#             'title': 'Post de prueba para loggueados',
#             'content': 'You gotta be logged in',
#             'public_access': 'None',
#             'authenticated_access': "None",
#             'group_access': "Read and Edit",
#             'author_access': "Read and Edit",
#         }
#          # Crear el post autenticado
#         self.client.post(reverse('blogpost-list'), postdata, content_type='application/json')
#         self.post_de_prueba = BlogPost.objects.get(title = "Post de prueba para loggueados")

#         postdata_soloread = {
#             'title': 'Post de prueba que solo se lee',
#             'content': 'Only the author can edit this post',
#             'public_access': 'None',
#             'authenticated_access': "None",
#             'group_access': "Read",
#             'author_access': "Read and Edit",
#         }
#         self.client.post(reverse('blogpost-list'), postdata_soloread, content_type='application/json')

#         self.postdata_soloread = BlogPost.objects.get(title = "Post de prueba que solo se lee")

#         postdata_soloauthor = {
#             'title': 'Post de prueba que solo puede leer el autor',
#             'content': 'Only the author can read this post',
#             'public_access': 'None',
#             'authenticated_access': "None",
#             'group_access': "None",
#             'author_access': "Read and Edit",
#         }
#         self.client.post(reverse('blogpost-list'), postdata_soloauthor, content_type='application/json')

#         self.postdata_soloauthor = BlogPost.objects.get(title = "Post de prueba que solo puede leer el group")

#         self.client.logout()

#     def test_read_and_edit_permissions(self):

#         self.client.login(username='prueba2', password='prueba1234')
        
#         response_get =self.client.get(reverse('blogpost-list'))
#         self.assertEqual(response_get.status_code, status.HTTP_200_OK)

#         response_get2 =self.client.get(reverse('blogpost-detail', args=[self.post_de_prueba.id]))
#         self.assertEqual(response_get2.status_code, status.HTTP_200_OK)

#         postdata = {
#             'title': 'Post de prueba para loggueados',
#             'content': 'You gotta be logged in edit: prueba2', #modified
#             'public_access': 'None',
#             'authenticated_access': "Read and Edit",
#             'group_access': "Read and Edit",
#             'author_access': "Read and Edit",
#         }
#         response_put = self.client.put(reverse('blogpost-detail', args=[self.post_de_prueba.id]), 
#                                        postdata, content_type="application/json")
#         self.assertEqual(response_put.status_code, status.HTTP_200_OK)
#         postdata = {
#             'title': 'Post de prueba para loggueados Edit: prueba 2 patch', #modified
#             'public_access': 'Read', #modified
#         }
#         response_patch = self.client.patch(reverse('blogpost-detail', args=[self.post_de_prueba.id]), 
#                                        postdata, content_type="application/json")
#         self.assertEqual(response_patch.status_code, status.HTTP_200_OK, "Error al actualizar el post")
#         response_delete = self.client.delete(reverse('blogpost-detail', args=[self.post_de_prueba.id]))
#         self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT, "Error al borrar el post")

#         response_get =self.client.get('blogpost-detail', args=[self.post_de_prueba.id])
#         self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND) #hacer esta prueba luego, creo que se debería ubicar mejor

#     def test_read_permissions(self):
#         self.client.login(username='prueba2', password='prueba1234')

#         response_get2 =self.client.get(reverse('blogpost-detail', args=[self.postdata_soloread.id]))
#         self.assertEqual(response_get2.status_code, status.HTTP_200_OK)

#         postdata_soloread = {
#             'title': 'Post de prueba que solo se lee',
#             'content': 'Only the author can edit this post',
#             'public_access': 'None',
#             'authenticated_access': "Read",
#             'group_access': "Read",
#             'author_access': "Read and Edit",
#         }
#         response_put = self.client.put(reverse('blogpost-detail', args=[self.postdata_soloread.id]), 
#                                        postdata_soloread, content_type="application/json")
#         self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)
#         postdata_soloread = {
#             'title': 'Post de prueba que solo se lee Edit: prueba 2 patch', #modified
#             'public_access': 'Read', #modified
#         }
#         response_patch = self.client.patch(reverse('blogpost-detail', args=[self.postdata_soloread.id]), 
#                                        postdata_soloread, content_type="application/json")
#         self.assertEqual(response_patch.status_code, status.HTTP_403_FORBIDDEN, "Error al actualizar el post")
#         response_delete = self.client.delete(reverse('blogpost-detail', args=[self.postdata_soloread.id]))
#         self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN, "Error al borrar el post")

#     def test_none_permissions(self):
#         self.client.login(username='prueba3', password='prueba12345')

#         response_get2 =self.client.get(reverse('blogpost-detail', args=[self.postdata_soloteam.id]))
#         self.assertEqual(response_get2.status_code, status.HTTP_404_NOT_FOUND)

#         postdata_soloteam = {
#             'title': 'Post de prueba que solo puede leer el group',
#             'content': 'Only the group can read, but not edit, this post',
#             'public_access': 'None',
#             'authenticated_access': "None",
#             'group_access': "Read",
#             'author_access': "Read and Edit",
#         }
#         response_put = self.client.put(reverse('blogpost-detail', args=[self.postdata_soloteam.id]), 
#                                        postdata_soloteam, content_type="application/json")
#         self.assertEqual(response_put.status_code, status.HTTP_404_NOT_FOUND)
#         postdata_soloteam = {
#             'title': 'Post de prueba que solo puede leer el group Edit: prueba 2 patch', #modified
#             'public_access': 'Read', #modified
#         }
#         response_patch = self.client.patch(reverse('blogpost-detail', args=[self.postdata_soloteam.id]), 
#                                        postdata_soloteam, content_type="application/json")
#         self.assertEqual(response_patch.status_code, status.HTTP_404_NOT_FOUND, "Error al actualizar el post")
#         response_delete = self.client.delete(reverse('blogpost-detail', args=[self.postdata_soloteam.id]))
#         self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND, "Error al borrar el post")