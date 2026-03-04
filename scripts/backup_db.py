#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Save (backup) the current database.

- SQLite: copies db.sqlite3 to backups/db_YYYYMMDD_HHMMSS.sqlite3
- PostgreSQL: runs pg_dump and saves to backups/vuvoz_YYYYMMDD_HHMMSS.sql
  (requires DATABASE_URL and pg_dump on PATH)

Creates a 'backups' directory in the project root if it does not exist.
Works on Windows and Unix.

Run from project root:
  python scripts/backup_db.py
  python scripts/backup_db.py C:\\my_backups
"""
import os
import shutil
import subprocess
import sys
from datetime import datetime

if __name__ == '__main__':
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(_script_dir)
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vuvoz.settings')
    import django
    django.setup()

from django.conf import settings


def run(output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db = settings.DATABASES['default']
    engine = db['ENGINE']

    if 'sqlite' in engine:
        src = db['NAME']
        if not os.path.isabs(str(src)):
            src = os.path.join(settings.BASE_DIR, str(src))
        src = os.path.normpath(src)
        dest = os.path.join(output_dir, f'db_{timestamp}.sqlite3')
        shutil.copy2(src, dest)
        print(f'Резервная копия SQLite сохранена: {dest}')
        return dest

    if 'postgresql' in engine:
        try:
            name = db.get('NAME', '')
            user = db.get('USER', '')
            password = db.get('PASSWORD', '')
            host = db.get('HOST', 'localhost') or 'localhost'
            port = db.get('PORT', '5432') or '5432'
            out_path = os.path.join(output_dir, f'vuvoz_{timestamp}.sql')
            env = os.environ.copy()
            if password:
                env['PGPASSWORD'] = str(password)
            cmd = ['pg_dump', '-h', host, '-p', str(port), '-U', user or os.environ.get('USER', ''), '-d', name]
            with open(out_path, 'w', encoding='utf-8') as f:
                subprocess.run(cmd, stdout=f, check=True, env=env)
            print(f'Резервная копия PostgreSQL сохранена: {out_path}')
            return out_path
        except FileNotFoundError:
            print('Ошибка: pg_dump не найден. Установите PostgreSQL client и добавьте в PATH.')
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f'Ошибка pg_dump: {e}')
            sys.exit(1)

    print(f'Резервное копирование для движка {engine} не реализовано.')
    sys.exit(1)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else None
    run(out)
