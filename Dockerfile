FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --omit=optional
COPY frontend/ ./
RUN npm run build

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
