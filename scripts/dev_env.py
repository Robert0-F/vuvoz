"""Helpers for local dev scripts (test passwords from root .env)."""
import os
import warnings

from dotenv import load_dotenv


def _project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_project_env():
    load_dotenv(_project_root() / '.env', override=False)


def get_dev_test_password():
    """
    Password for test users in load_test_data / setup_dev_data.
    Only allowed when DJANGO_DEBUG is True.
    """
    load_project_env()
    debug = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')
    try:
        from django.conf import settings

        debug = settings.DEBUG
    except Exception:
        pass

    if not debug:
        raise RuntimeError(
            'Test data scripts must not run with DJANGO_DEBUG=False. '
            'Use local .env with DJANGO_DEBUG=True and DEV_TEST_PASSWORD for development only.'
        )

    password = os.environ.get('DEV_TEST_PASSWORD', 'test123')
    if password == 'test123':
        warnings.warn(
            'Using default DEV_TEST_PASSWORD=test123. Set DEV_TEST_PASSWORD in .env to override.',
            stacklevel=2,
        )
    return password
