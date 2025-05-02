from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=User)
def customer_profile(sender, instance, created, **kwargs):
  if created:
    Customer.objects.create(
      user = instance, 
      username = instance.username, 
      first_name = instance.first_name,
      last_name = instance.last_name,
      email = instance.email,
      
    )

post_save.connect(customer_profile, sender=User)

