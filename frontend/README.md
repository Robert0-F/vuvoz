# Waste Paper Collection — Frontend

Vue 3 + Vite + TypeScript + Vuetify 3 + Pinia + Vue Router + Axios.

## Setup

```bash
npm install
```

## Development

Start the backend (from project root):

```bash
python manage.py runserver
```

Start the frontend (with proxy to backend at `http://localhost:8000`):

```bash
npm run dev
```

Open http://localhost:5173. Log in with a company or institution user.

## Build

```bash
npm run build
```

## Auth

- JWT: login with username/password at `/api/token/`; access token is stored in `localStorage` and sent via `Authorization: Bearer <token>`.
- After login, `/api/me/` is used to get user and role-specific profile; redirect is based on `user.role` (company → `/company`, institution → `/institution`).
