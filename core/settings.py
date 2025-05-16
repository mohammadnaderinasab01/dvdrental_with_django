from django.contrib.auth.hashers import PBKDF2PasswordHasher
from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # internal apps
    'films',
    'customer',
    'payment',
    'store',
    'users',
    'admin_panel',
    'store_staff_panel',
    'database_profiler',

    # external apps
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'database_profiler.middleware.DatabaseMonitoringMiddleware',
]


class CustomPBKDF2PasswordHasher(PBKDF2PasswordHasher):
    iterations = 260000


PASSWORD_HASHERS = [
    'core.settings.CustomPBKDF2PasswordHasher',
]

# djangorestframework configuration
REST_FRAMEWORK = {
    # authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],

    # schema
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # filter backends
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

    # pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

    # throttling
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/hour',
        'user': '10000/hour'
    },
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
}


# cors-headers configuration
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


# drf-spectacular configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'DVDRental API',
    'DESCRIPTION': '',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True
    # OTHER SETTINGS
}

# cache config
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv('REDIS_URL'),  # Redis server address and database (e.g., 1)
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": os.getenv("REDIS_PASSWORD"),  # If Redis requires a password
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "MAX_CONNECTIONS": os.getenv('REDIS_MAX_CONNECTIONS'),
        },
    }
}

# Celery Configuration
CELERY_BROKER_URL = f'redis://:{os.getenv("REDIS_PASSWORD")}@localhost:6379/0'  # Redis as the broker
CELERY_RESULT_BACKEND = f'redis://:{os.getenv("REDIS_PASSWORD")}@localhost:6379/0'  # Redis as the result backend
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'  # Or your desired timezone
CELERY_ENABLE_UTC = True

# Optional: Beat Scheduler for periodic tasks
CELERY_BEAT_SCHEDULE = {
    'send-overdue-notifications': {
        'task': 'admin_panel.tasks.send_inventory_rental_overdue_email',
        'schedule': 60 * 60 * 24,  # Run every day (in seconds)
    },
    'send-activity-email-for-inactive-customers': {
        'task': 'admin_panel.tasks.inactive_customers_activity_email_notifier',
        'schedule': 60 * 60 * 24,  # Run every day (in seconds)
    },
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'celery_tasks.log',  # Logs will be written to this file
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'admin_panel.tasks': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'customer.tasks': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'database_profiler.tasks': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# notifier email Configuration
MAIL_SERVER_HOST = os.getenv('MAIL_SERVER_HOST')
NOTIFIER_EMAIL_ADDRESS = os.getenv('NOTIFIER_EMAIL_ADDRESS')
NOTIFIER_EMAIL_PASSWORD = os.getenv('NOTIFIER_EMAIL_PASSWORD')

AUTH_USER_MODEL = 'users.User'

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv('DATABSE_NAME'),
        "USER": os.getenv('DATABSE_USERNAME'),
        "PASSWORD": os.getenv('DATABSE_SECRET'),
        "HOST": os.getenv('DATABSE_HOSTNAME'),
        "PORT": os.getenv('DATABSE_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
