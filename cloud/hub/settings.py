import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'aiota-secret-key-xcMWc89ypB6T0Ku0kXVrCmvhHVwMu6ZT'
DEBUG = True
ALLOWED_HOSTS = ['aiota.akilinova.co.ke', '127.0.0.1', 'localhost', '15.235.183.163']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

QDRANT_URL = 'https://e2a8ca0e-e4da-465b-8485-eb24b83d768f.us-central1-0.gcp.cloud.qdrant.io'
QDRANT_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6ODdlZjUxYzUtYmU5My00NWVhLWIwNWQtNzIwMTU1MGRiNzAzIn0.dhuPjOol7P3tSGSDOwReMMm-FcxudYs2iClmCADGibQ'

NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY', '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')
NVIDIA_MODEL = os.getenv('NVIDIA_MODEL', 'meta/llama-3.2-90b-vision-instruct')

