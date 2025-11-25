from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Create a superuser with the specified username, email, and password'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Username for the superuser'
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email for the superuser'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Password for the superuser'
        )
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Replace existing superuser with the same username'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        replace = options['replace']

        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                if replace:
                    # Delete existing user
                    user = User.objects.get(username=username)
                    user.delete()
                    self.stdout.write(
                        self.style.WARNING(f'Deleted existing user: {username}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Superuser with username "{username}" already exists.')
                    )
                    self.stdout.write(
                        self.style.WARNING('Use --replace flag to replace the existing user.')
                    )
                    return

            # Create the superuser
            superuser = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Superuser created successfully!'
                )
            )
            self.stdout.write(f'Username: {superuser.username}')
            self.stdout.write(f'Email: {superuser.email}')
            self.stdout.write(f'Is staff: {superuser.is_staff}')
            self.stdout.write(f'Is superuser: {superuser.is_superuser}')

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'IntegrityError: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )