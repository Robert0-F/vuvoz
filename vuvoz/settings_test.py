"""
Test settings: SQLite in-memory DB (no PostgreSQL CREATEDB required).
Used by pytest via pytest.ini.
"""
from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# APIClient uses HTTP_HOST=testserver
ALLOWED_HOSTS = list(set(ALLOWED_HOSTS + ['testserver', 'localhost', '127.0.0.1']))

# Faster password hashing in tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
