from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a normal user if not exists'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(username="testuser").exists():
            User.objects.create_user(
                username="testuser",
                email="testuser@example.com",
                password="testpassword123"
            )
            self.stdout.write(self.style.SUCCESS("Normal user created"))
        else:
            self.stdout.write(self.style.WARNING("User already exists"))
