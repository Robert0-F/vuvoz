#!/usr/bin/env python
"""
Simple health check for Vuvoz.
Run: python scripts/health_check.py
Exits 0 if OK, 1 otherwise.
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vuvoz.settings')

def main():
    try:
        import django
        django.setup()
        from django.db import connection
        connection.ensure_connection()
        connection.close()
        print("OK")
        return 0
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
