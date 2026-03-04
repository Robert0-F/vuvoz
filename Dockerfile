# Debian-based Node (glibc) so Rollup's native binding can be installed
FROM node:20-slim AS frontend
WORKDIR /app/frontend
ENV SASS_SILENCE_DEPRECATION=legacy-js-api
ENV NODE_OPTIONS=--max-old-space-size=4096
COPY frontend/ ./
COPY frontend/.env.production ./
# Reinstall node_modules in container so optional platform binary (@rollup/rollup-linux-x64-gnu)
# is installed for Linux (lockfile from Windows skips it - npm optionalDeps bug #4828)
RUN rm -rf node_modules && npm install && npm run build

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn dj-database-url

COPY --from=frontend /app/frontend/dist /app/frontend/dist
COPY . .

EXPOSE 8000
CMD ["gunicorn", "vuvoz.wsgi:application", "--bind", "0.0.0.0:8000"]
