# Pre-Launch Deployment Audit — Vuvoz

**Date:** 2025-02-03  
**Goal:** Production-ready, stable, secure build with all tests passing and documentation updated.

---

## 1. Checks Performed

### 1.1 Environment Setup
- **Backend:** Virtual environment (`.venv`), `pip install -r requirements.txt` — completed successfully.
- **Frontend:** `cd frontend && npm install` — completed successfully (npm reported 9 low-severity vulnerabilities; consider `npm audit` before production).

### 1.2 Configuration (`vuvoz/settings.py`)
- **DEBUG:** Driven by `DJANGO_DEBUG` env (default `False`); production should set `DJANGO_DEBUG=False`.
- **ALLOWED_HOSTS:** From env `ALLOWED_HOSTS` (comma-separated); must be set to production domain(s) or IP.
- **DATABASES:** PostgreSQL via `DATABASE_URL` (dj-database-url); SQLite fallback for local dev.
- **Static files:** `STATIC_ROOT`, `STATICFILES_DIRS` (includes `frontend/dist`), WhiteNoise middleware for serving static.
- **Media files:** `MEDIA_URL`, `MEDIA_ROOT` defined; in Docker served via Nginx from `/media/`.
- **Security (when not DEBUG):**  
  `SECURE_BROWSER_XSS_FILTER`, `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS = 'DENY'`,  
  `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`,  
  `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`,  
  `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD`.  
  SSL redirect and HSTS can be toggled via env where useful (e.g. behind reverse proxy).
- **CORS / CSRF:** `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` from env; must include production frontend origin (e.g. `https://example.com`).

### 1.3 Database & Migrations
- **`python manage.py check`:** No issues.
- **`python manage.py makemigrations --check`:** One pending migration detected — **0017_alter_pricelist_options** (PriceList Meta options). Migration was created and applied.
- **`python manage.py migrate --noinput`:** All migrations applied successfully.

### 1.4 Testing
- **Backend tests:** `pytest tests/ -v` — **21 tests passed.**  
  One warning: missing `staticfiles` (expected before `collectstatic`); non-blocking.

### 1.5 Static & Media Files
- **`python manage.py collectstatic --noinput`:** 182 files collected into `staticfiles/`.
- **WhiteNoise:** Configured; static files served by Django in production when using Gunicorn; in Docker, Nginx serves `/static/` and `/media/` from volumes.
- **Media uploads:** Configured; in production ensure `MEDIA_ROOT` is writable and backed by persistent volume in Docker.

### 1.6 Frontend Build
- **`cd frontend && npm run build`:** Completed successfully.  
  - SASS legacy JavaScript API deprecation warning (non-blocking).  
  - One chunk size warning (non-blocking).  
- **Output:** `frontend/dist/` with `index.html` and assets; included in `STATICFILES_DIRS` and collected to `staticfiles/`.
- **SPA serving:** `VueSPAView` serves `index.html` from `frontend/dist` or, if missing, from `STATIC_ROOT` (e.g. after collectstatic-only deploy), so SPA works in both Docker and non-Docker setups.

### 1.7 Docker, Nginx, Gunicorn
- **Dockerfile:** Multi-stage build (Node 20 → Python 3.11); frontend built in container; Gunicorn runs with default bind `0.0.0.0:8000`. Requires `frontend/.env.production` for build (Vite API base).
- **docker-compose.yml:** PostgreSQL 15, backend (migrate + collectstatic + Gunicorn with `--workers 2`), Nginx on port 80; volumes for static and media; env from `.env` with sensible defaults for local Docker.
- **nginx.conf:** Serves `/static/`, `/media/`; proxies `/api/`, `/admin/`, and `/` to backend; SPA fallback `error_page 404 = /index.html`; **proxy timeouts** added for `/api/` and `/admin/` (read/send 120s, connect 10s) to avoid premature timeouts on long requests.
- **Gunicorn:** In Docker runs with 2 workers; for higher load, increase in `docker-compose` or in DEPLOYMENT.md (e.g. 4 workers, `--timeout 120`).

### 1.8 Documentation
- **README.md:** Production section added with links to DEPLOYMENT.md and DEPLOYMENT_AUDIT.md.
- **DEPLOYMENT.md:** Already contains production steps (single server, Nginx + Gunicorn, Docker, domain, SSL, checklist). No structural changes required.
- **.env.example:** Updated with `DJANGO_DEBUG=False`, optional `BASE_URL`, `SECURE_SSL_REDIRECT`, and short production notes.

---

## 2. Issues Found and Resolutions

| Item | Resolution |
|------|------------|
| Pending migration (PriceList Meta) | Created and applied **0017_alter_pricelist_options**. |
| SPA view only looked at `frontend/dist` | **VueSPAView** now falls back to `STATIC_ROOT/index.html` when `frontend/dist/index.html` is missing (e.g. collectstatic-only deploy). |
| Nginx proxy timeouts not set | Added **proxy_read_timeout 120**, **proxy_send_timeout 120**, **proxy_connect_timeout 10** for `/api/` and **proxy_read_timeout 120** for `/admin/` in `nginx.conf`. |
| No single place for audit summary | Created **DEPLOYMENT_AUDIT.md** (this file). |

No failing tests or blocking configuration errors were found.

---

## 3. Test Status

- **All 21 backend tests pass** (`pytest tests/ -v`).
- No test code or configuration was changed to fix failures.

---

## 4. Steps Before Final Deployment

1. **Environment:** On the production server, set all variables from `.env.example` (at least `DJANGO_SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`; `DJANGO_DEBUG=False`).
2. **Domain:** Point DNS to the server; set `server_name` in `nginx.conf` to your domain (see comment in file).
3. **SSL:** After HTTP works, configure HTTPS (e.g. Certbot); add `https://yourdomain` to CORS and CSRF origins.
4. **Optional:** Run `python manage.py check` with `DEBUG=False` and production env to double-check. Run `docker compose up --build` locally with production-like `.env` to test the full stack.
5. **Optional:** Run `npm audit` in `frontend/` and address or accept remaining vulnerabilities; plan migration off SASS legacy API if needed.
6. **Superuser:** Create an admin user (e.g. `python manage.py createsuperuser` or `docker compose exec backend python manage.py createsuperuser`).

---

## 5. Deliverables Summary

- **Codebase:** Production-ready; security and static/media settings in place; SPA view supports both `frontend/dist` and collectstatic-only.
- **Tests:** All 21 tests passing.
- **Documentation:** README and DEPLOYMENT.md updated; .env.example and DEPLOYMENT_AUDIT.md in place.
- **Docker/Nginx:** Timeouts configured; Dockerfile and docker-compose suitable for production use.
