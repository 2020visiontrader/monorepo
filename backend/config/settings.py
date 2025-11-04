"""
Django settings for ecommerce optimizer project.
"""
import os
from pathlib import Path
import environ

env = environ.Env(
    DEBUG=(bool, False),
    ENVIRONMENT=(str, 'ST'),
)

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=True)

ENVIRONMENT = env('ENVIRONMENT', default='ST')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',
    'brands',
    'competitors',
    'content',
    'seo',
    'frameworks',
    'shopify',
    'llm',
    'store_templates',
    'dashboard',
    'ai',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.TenancyMiddleware',
    'core.middleware.RBACMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='ecommerce_optimizer'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='postgres'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserPasswordValidator',
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/hour',
        'content_generate': '10/minute',
        'competitor_recrawl': '3/minute',
        'job_logs': '60/minute',
    },
}

# CORS
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
    'http://127.0.0.1:3000',
])
CORS_ALLOW_CREDENTIALS = True

# CSRF settings for same-site dev
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['http://localhost:3000', 'http://127.0.0.1:3000'])

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Redis
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/1')

# Shopify
SHOPIFY_API_KEY = env('SHOPIFY_API_KEY', default='')
SHOPIFY_API_SECRET = env('SHOPIFY_API_SECRET', default='')
SHOPIFY_API_VERSION = env('SHOPIFY_API_VERSION', default='2024-01')
SHOPIFY_REDIRECT_URI = env('SHOPIFY_REDIRECT_URI', default='http://localhost:8000/api/shopify/callback')

# LLM
LLM_PROVIDER = env('LLM_PROVIDER', default='mock')  # mock, openai, anthropic
LLM_API_KEY = env('LLM_API_KEY', default='')
LLM_MODEL = env('LLM_MODEL', default='gpt-4-turbo-preview')
LLM_USE_MOCK = env.bool('LLM_USE_MOCK', default=(ENVIRONMENT in ['ST', 'SIT']))

# AI Framework Integration (Abacus-backed)
AI_FRAMEWORKS_ENABLED = env.bool('AI_FRAMEWORKS_ENABLED', default=False)
AI_SHADOW_MODE = env.bool('AI_SHADOW_MODE', default=True)  # Run in background, don't affect responses
AI_AUTOPILOT_ENABLED = env.bool('AI_AUTOPILOT_ENABLED', default=False)
AI_PROVIDER = env('AI_PROVIDER', default='abacus')

# Per-framework flags (dict format: {"product_copy": true, "seo": false, ...})
# Override global flags when present
# Parse JSON string from env or use empty dict
def _parse_framework_flags(env_key: str) -> dict:
    """Parse per-framework flags from environment"""
    import json
    env_value = env(env_key, default='{}')
    try:
        return json.loads(env_value) if env_value else {}
    except (json.JSONDecodeError, TypeError):
        return {}

AI_FRAMEWORKS_ENABLED_BY_NAME = _parse_framework_flags('AI_FRAMEWORKS_ENABLED_BY_NAME')
AI_SHADOW_MODE_BY_NAME = _parse_framework_flags('AI_SHADOW_MODE_BY_NAME')
AI_USE_MOCK_BY_FRAMEWORK = _parse_framework_flags('AI_USE_MOCK_BY_FRAMEWORK')

# Cache settings
AI_CACHE_TTL_DAYS = env.int('AI_CACHE_TTL_DAYS', default=7)
AI_POLICY_VERSION = env('AI_POLICY_VERSION', default='1.0')  # Increment to invalidate cache

# Feature Flags
FEATURE_FLAGS = {
    'store_templates': env.bool('FEATURE_STORE_TEMPLATES', default=(ENVIRONMENT in ['UAT', 'PROD'])),
}

# Limits
MAX_VARIANTS = 3
MAX_COMPETITOR_PAGES = 10
MAX_COMPETITOR_PAGES_SINGLE_SKU = 5

