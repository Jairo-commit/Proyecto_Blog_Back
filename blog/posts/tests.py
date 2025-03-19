from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User


from .models import BlogPost

# Create your tests here.

class PostTestCase(TestCase):

    def setUp(self):
        print("haciendo el setup")
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
            'password': 'prueba123',
            'first_name': 'nombre2',
            'last_name': 'apellido2',
            'email': 'example2@example.com'
        }

        self.client.post(reverse('user_register-list'), self.user_data2)
        self.user2 = User.objects.get(username = self.user_data2['username'])

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
        print("primer post del setup ",self.post_de_prueba.id)
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
        print("segundo post del setup ",self.postdata_soloread.id)

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
        print("tercer post del setup ",self.postdata_soloteam.id)

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

        #probando el nuevo workflow de github con este mensaje... preguntar a Jose si crear varias clases de testcases?