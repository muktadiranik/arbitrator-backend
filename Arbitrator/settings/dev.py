import os

from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['34.225.214.96', '67.207.93.188', '127.0.0.1', 'localhost', '0.0.0.0', '18.234.139.114',
                 'ec2-18-234-139-114.compute-1.amazonaws.com', 'api.arbitrationagreement.com', '34.225.99.96']

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
    }
}

REST_FRAMEWORK.update({
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.authentications.CsrfExemptSessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ]
})

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://localhost:4300",
    "http://127.0.0.1:4200",
    "http://127.0.0.1:4300",
    "http://localhost:80",
    "http://67.207.93.188:8081",
    "http://34.225.214.96:4200",
    "http://18.234.139.114:4200",
    "https://arbitrationagreement.com",
    "https://www.arbitrationagreement.com",
    "https://api.arbitrationagreement.com"
]

CSRF_TRUSTED_ORIGINS = [
    "http://67.207.93.188:8081",
    "http://34.225.214.96:4200",
    "http://localhost:4200",
    "http://localhost:4300",
    "http://127.0.0.1:4200",
    "http://127.0.0.1:4300",
    "http://localhost:80",
    "http://18.234.139.114:4200",
    "https://arbitrationagreement.com",
    "https://www.arbitrationagreement.com",
    "https://api.arbitrationagreement.com"
]

# CELERY CONFIGURATION
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
CELERY_BROKER_URL = f'redis://:{REDIS_PASSWORD}@arbitrator-backend-dev-redis:6379/1'  # with password
CELERY_RESULT_BACKEND = f'redis://:{REDIS_PASSWORD}@arbitrator-backend-dev-redis:6379/1'
ASGI_APPLICATION = "arbitrator.routing.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(f'redis://:{REDIS_PASSWORD}@arbitrator-backend-dev-redis:6379/0')],
        },
    },
}

ACTSTREAM_SETTINGS = {
    'USE_PREFETCH': True,
    "USE_JSONFIELD": True,
}
