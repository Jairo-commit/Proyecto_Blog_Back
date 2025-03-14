from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

@receiver(m2m_changed, sender=User.groups.through)
def enforce_exactly_one_group(sender, instance, action, pk_set, **kwargs):
    
    if action == "post_add":
        if instance.groups.count() > 1:
            raise ValueError("Cada usuario debe pertenecer a un solo grupo. No puede tener más de uno.")


