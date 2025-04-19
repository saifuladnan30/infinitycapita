from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import MemberFinance

@receiver(post_save, sender=User)
def create_finance_record(sender, instance, created, **kwargs):
    if created:
        MemberFinance.objects.create(user=instance)
