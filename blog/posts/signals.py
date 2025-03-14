from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import BlogPost 

@receiver(pre_save, sender=BlogPost)
def generate_excerpt(sender, instance, **kwargs):
    """
    Automatically generate an excerpt from the content before saving a BlogPost.
    """
    instance.excerpt = instance.content[0:200]
    
