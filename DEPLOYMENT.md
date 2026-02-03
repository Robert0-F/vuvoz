# Deployment Guide

## Local development

1. **Backend**
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

2. **Frontend** (separate terminal)
   ```bash
   cd frontend && npm install && npm run dev
   ```
   Open http://localhost:5173 (Vite proxies `/api` to port 8000).

3. **Test data**
   ```bash
   python -c "exec(open('setup_dev_data.py').read()); run()"
   ```
   Or from Django shell: `exec(open('setup_dev_data.py').read())` then `run()`.
   - Company: `company@test.com` / `test123`
   - Institution: `school1@test.com` / `test123`

## Single-server production (Django serves Vue)

1. Build frontend and collect static:
   ```bash
   bash build_frontend.sh   # or: cd frontend && npm run build
   python manage.py collectstatic --noinput
   python manage.py migrate --noinput
   ```

2. Run with Gunicorn:
   ```bash
   gunicorn vuvoz.wsgi:application --bind 0.0.0.0:8000
   ```
   Open http://localhost:8000 (SPA at `/`, API at `/api/`, static at `/static/`).

3. Environment variables (optional):
   - `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`
   - `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`
   - `DATABASE_URL` for PostgreSQL (e.g. `postgres://user:pass@host/db`)
   - `EMAIL_BACKEND` for production email

## Docker (PostgreSQL + Django + Nginx)

1. Create `.env` from `.env.example` and set `POSTGRES_PASSWORD`, `DJANGO_SECRET_KEY`.

2. Build and run:
   ```bash
   docker compose up --build
   ```
   App at http://localhost (port 80). Nginx serves static and proxies API to Django.

## Tests

```bash
pytest tests/ -v
```

## Postman

Import `postman_collection.json`. Set `base_url` to `http://localhost:8000/api` and `access_token` after obtaining a token from `POST /api/token/`.
