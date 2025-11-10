"""
Test settings for ecommerce optimizer project.
Uses SQLite for testing instead of PostgreSQL.
"""
import os
from .settings import *

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable debug for tests
DEBUG = False

# Use in-memory email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'WARNING',
        },
    },
}

# Disable password validation for tests
AUTH_PASSWORD_VALIDATORS = []
