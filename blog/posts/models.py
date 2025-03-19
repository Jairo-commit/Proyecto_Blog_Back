from django.db import models
from django.contrib.auth.models import User


class BlogPost(models.Model):
    ACCESS_CHOICES = [
        ('None', 'None'),
        ('Read', 'Read'),
        ('Read and Edit', 'Read and Edit'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    excerpt = models.TextField(default='No Excerpt')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Permisos por nivel de acceso
    public_access = models.CharField(max_length=15, choices=[('None', 'None'),('Read', 'Read')])
    authenticated_access = models.CharField(max_length=15, choices=ACCESS_CHOICES, default='Read')
    group_access = models.CharField(max_length=15, choices=ACCESS_CHOICES, default='Read')
    author_access = models.CharField(max_length=15, choices=[('Read and Edit', 'Read and Edit')])

    class Meta:
        ordering = ['-created_at']  # Ordena los posts por fecha de creación (más recientes primero)

    def __str__(self):
        return self.title

    def get_author_group(self):
        """
        Retorna el grupo del autor del post. Si el autor no tiene grupo, retorna None.
        """
        return self.author.groups.first()
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save() para aplicar la jerarquía de permisos.
        - author_access siempre debe ser "Read and Edit".
        - Si la jerarquía de permisos es violada, lanza un ValueError.
        """
        access_levels = ['None', 'Read', 'Read and Edit']

        # Convierte los permisos en índices para comparar jerarquía
        public_level = access_levels.index(self.public_access)
        authenticated_level = access_levels.index(self.authenticated_access)
        group_level = access_levels.index(self.group_access)
        author_level = access_levels.index(self.author_access)

        # Validaciones de jerarquía
        if authenticated_level < public_level:
            raise ValueError("Authenticated access no puede ser menor que Public access.")
        if group_level < authenticated_level:
            raise ValueError("Group access no puede ser menor que Authenticated access.")
        if author_level < group_level:
            raise ValueError("Author access no puede ser menor que Group access.")
        
        super().save(*args, **kwargs)

