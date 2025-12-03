import os
import sys
import logging
import django
from django.contrib.auth import get_user_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()
User = get_user_model()

username = os.getenv('DJANGO_SUPERUSER_USERNAME')
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

if not all([username, email, password]):
    logger.warning("No superuser variables provided")
else:
    if User.objects.filter(username=username).exists():
        logger.info("Superuser already exists. Skipping")
    else:
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            logger.info("Superuser created")
        except Exception as e:
            logger.error(f"Error during creating superuser: {e}")
            sys.exit(1)
