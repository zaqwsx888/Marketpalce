from django.core.management.base import BaseCommand
from app_users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@admin.ru'
        password = 'admin'
        if not User.objects.filter(username=username).exists():
            print('Creating account for %s (%s)' % (username, email))
            admin = User.objects.create_superuser(
                email=email, username=username, password=password
            )
            admin.is_active = True
            admin.is_admin = True
            admin.slug = 'admin'
            admin.save()
        else:
            print(
                'Admin accounts can only be initialized if no Accounts exist'
            )
