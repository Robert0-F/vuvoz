#!/usr/bin/env python
"""
Verify required variables in .env before production deploy.

Usage (from project root):
  python scripts/check_env.py
"""
import os
import sys
from pathlib import Path

_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from dotenv import load_dotenv

load_dotenv(_project_root / '.env', override=False)

_INSECURE_SECRET = 'django-insecure-change-in-production'
_PLACEHOLDERS = ('CHANGE_ME', 'your-secret-key', 'vuvoz_secret')


def _get(name):
    return (os.environ.get(name) or '').strip()


def _is_placeholder(value):
    if not value:
        return True
    lower = value.lower()
    return any(p.lower() in lower for p in _PLACEHOLDERS)


def main():
    errors = []
    warnings = []

    debug = _get('DJANGO_DEBUG').lower() in ('true', '1', 'yes')

    secret = _get('DJANGO_SECRET_KEY')
    if _is_placeholder(secret) or secret == _INSECURE_SECRET:
        errors.append('DJANGO_SECRET_KEY: set a unique value (openssl rand -base64 50)')

    if not debug:
        if not _get('DATABASE_URL'):
            errors.append('DATABASE_URL: required when DJANGO_DEBUG=False')
        elif _is_placeholder(_get('DATABASE_URL')):
            errors.append('DATABASE_URL: replace CHANGE_ME with real PostgreSQL credentials')

        if not _get('ALLOWED_HOSTS'):
            errors.append('ALLOWED_HOSTS: required for production')

        if _get('DEV_TEST_PASSWORD'):
            warnings.append('DEV_TEST_PASSWORD is set; remove it on production servers')
    else:
        if not _get('DATABASE_URL'):
            warnings.append('DATABASE_URL not set; Django will use SQLite')

    if warnings:
        print('Warnings:')
        for w in warnings:
            print(f'  - {w}')
        print()

    if errors:
        print('Environment check FAILED:')
        for e in errors:
            print(f'  - {e}')
        sys.exit(1)

    print('Environment check OK.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
