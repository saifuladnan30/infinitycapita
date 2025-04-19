from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create default superuser if not exists"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="adminpassword"
            )
            self.stdout.write(self.style.SUCCESS("Superuser created."))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists."))
