import os
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    """
    Create a superuser automatically after migrations if none exists.
    Uses environment variables for configuration.
    """
    if sender.name == 'accounts':
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            # Debug: Print all environment variables
            print("DEBUG: Environment variables:")
            print(f"ROOT_EMAIL: {os.getenv('ROOT_EMAIL')}")
            print(f"ROOT_USERNAME: {os.getenv('ROOT_USERNAME')}")
            print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')}")
            print(f"DJANGO_SUPERUSER_PASSWORD: {os.getenv('DJANGO_SUPERUSER_PASSWORD')}")
            
            email = os.getenv('ROOT_EMAIL', 'admin@example.com')
            username = os.getenv('ROOT_USERNAME', 'admin')
            password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
            first_name = os.getenv('DJANGO_SUPERUSER_FIRST_NAME', 'Root')
            last_name = os.getenv('DJANGO_SUPERUSER_LAST_NAME', 'User')
            organization = os.getenv('DJANGO_SUPERUSER_ORGANIZATION', '')
            access_key_id = os.getenv('AWS_ACCESS_KEY_ID', '')
            secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', '')
            
            User.objects.create_superuser(
                email=email,
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='admin',
                organization=organization,
                access_key_id=access_key_id,
                secret_access_key=secret_access_key
            )
            print(f"Superuser created: {email}")