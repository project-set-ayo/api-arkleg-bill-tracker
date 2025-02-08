import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch DJANGO_ENV (default to "development" if not set)
DJANGO_ENV = os.getenv("DJANGO_ENV", "development").lower()

# Select settings module based on DJANGO_ENV
if DJANGO_ENV == "production":
    from .production import *
else:
    from .development import *
