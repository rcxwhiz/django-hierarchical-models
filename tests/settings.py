import os

SECRET_KEY = 'dummy'

INSTALLED_APPS = (
    'django_hierarchical_models',
    'tests',
)

if os.environ.get('POSTGRES'):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "dhm_db"),
            "USER": os.environ.get("POSTGRES_USER", 'dhm_user'),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432")
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

USE_TZ = True
