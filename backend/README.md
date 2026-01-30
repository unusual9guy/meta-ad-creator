# Meta Ad Creator — Backend API

FastAPI backend for the web app. Implements REST API and Supabase integration in **parts** (see [web-app-roadmap.md](../docs/web-app-roadmap.md)).

## Part 1 (current): Skeleton, health, CORS, auth

- **`GET /health`** — Public health check.
- **`GET /api/me`** — Protected; requires `Authorization: Bearer <supabase_access_token>`. Returns `{"user_id": "..."}`.

### Setup

1. From repo root or `backend/`:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```
2. Copy `backend/.env.example` to `backend/.env` and set:
   - `SUPABASE_URL` — Project Settings → API
   - `SUPABASE_SERVICE_ROLE_KEY` — Project Settings → API (service_role key)
   - `SUPABASE_JWT_SECRET` — Project Settings → API → JWT Secret
3. Run:
   ```bash
   uvicorn main:app --reload --app-dir backend
   ```
   Or from `backend/`:
   ```bash
   uvicorn main:app --reload
   ```
   API: http://localhost:8000. Docs: http://localhost:8000/docs.

### Testing auth

1. Sign in on the frontend (or get a token from Supabase Auth).
2. In browser dev tools or Postman, copy the session access token (e.g. from Supabase client: `supabase.auth.getSession()` → `session.access_token`).
3. `GET http://localhost:8000/api/me` with header: `Authorization: Bearer <access_token>`.

### Next part

Part 2: Projects CRUD — `GET /projects`, `POST /projects`, `GET /projects/:id`.
