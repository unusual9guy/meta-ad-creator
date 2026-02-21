# Meta Ad Creator — Web App Roadmap

A phased plan to turn the existing Streamlit + 5-agent Meta Ad Creator into a production web application with a minimal, professional frontend, REST API backend, and Supabase for database and auth.

---

## Status overview

| Phase | Focus       | Status   | Notes |
|-------|-------------|----------|--------|
| 0     | Discovery   | **Done** | Flows, schema, API contract, wireframes |
| 1     | Database    | **Done** | Supabase: tables, RLS, Storage migrations run |
| 2     | Backend     | **In progress** | Implemented in parts below |
| 3     | Frontend    | **Done** | Landing, Auth, Dashboard shell (list/detail UI left for later) |
| 4     | Integration | Pending  | E2E, deploy, docs |

### Phase 2 — Backend (incremental parts)

Backend is built part by part for easier tracking and commits.

| Part | Scope | Status |
|------|--------|--------|
| **2.1** | FastAPI app skeleton, `GET /health`, CORS, Supabase client (service role), JWT auth dependency | **Done** |
| 2.2 | Projects CRUD: `GET /projects`, `POST /projects`, `GET /projects/:id` (auth required) | Pending |
| 2.3 | Upload + first asset: create project with original image (Storage + `assets` row) | Pending |
| 2.4 | Workflow: `POST /projects/:id/analyze` (call product_analyser, update workflow_state) | Pending |
| 2.5 | Workflow: `POST /projects/:id/remove-background`, `POST /projects/:id/generate-prompt` | Pending |
| 2.6 | Workflow: `POST /projects/:id/generate-creative`; assets/signed URLs if needed | Pending |
| 2.7 | Optional: jobs/polling for long steps; Dockerfile for API | Pending |

---

## Goals

- **Product**: Public-facing web app where users sign up, run the ad-creation workflow, and manage creatives from a dashboard.
- **Database**: Supabase (PostgreSQL, Auth, Storage, optional Realtime).
- **Frontend**: Minimal, professional, not “vibe coded” — restrained typography, clear hierarchy, purposeful color, no generic AI-slop aesthetic.
- **Backend**: REST API that orchestrates the existing Python agents; stateless where possible; jobs for long-running creative generation.

---

## Design Principles (Frontend)

- **Minimal**: Plenty of whitespace, clear sections, no decorative clutter.
- **Professional**: Consistent spacing, readable type, accessible contrast.
- **Distinct**: Avoid default “AI app” look (e.g. Inter + purple gradients, generic hero). Choose a small, coherent font stack and a limited, intentional palette.
- **Functional**: Navigation and actions are obvious; loading and error states are explicit.

---

## Phase 0 — Discovery & Design (No Code) ✅ Done

**Objective**: Lock scope, flows, and contracts so Phase 1–3 stay aligned.

### 0.1 User flows (document only)

- **Anonymous**: Land on homepage → see value prop + CTA to sign up / sign in.
- **Auth**: Sign up (email + password), Sign in, Forgot password (email link or code).
- **Authenticated**: Dashboard → start new “Create ad” flow (upload image + inputs) → optional checkpoints (e.g. confirm analysis, confirm prompt) → final creative; list/history of projects/creatives; view/download/delete creatives.
- **Optional later**: Teams, workspaces, billing — explicitly out of scope for first version unless you decide otherwise.

### 0.2 Data model (for Supabase)

- **Users**: Handled by Supabase Auth (no custom `users` table unless you need extra profile fields).
- **Projects (or “Campaigns”)**: One per “run” of the workflow.
  - `id`, `user_id` (FK to auth.users), `name` (optional), `status` (draft | analysing | processing | ready | failed), `created_at`, `updated_at`.
  - Optional: `product_name`, `target_audience`, `promotion_text`, etc. for display in dashboard.
- **Assets**: Input and output files.
  - `id`, `project_id`, `type` (original_upload | background_removed | cropped | final_creative), `storage_path` (Supabase Storage key), `mime_type`, `created_at`.
- **Workflow state (optional)**: If you want to persist “step” and payloads for resume/audit.
  - e.g. `project_id`, `step` (analysis_done | bg_removed | prompt_generated | creative_generated), `payload` (JSON: product_persona, prompt_json, etc.), `updated_at`.

### 0.3 API contract (REST, high level)

- **Auth**: Supabase handles sign up / sign in / forgot password; backend only validates JWT on protected routes.
- **Projects**: `GET /projects`, `POST /projects`, `GET /projects/:id`.
- **Workflow**: `POST /projects/:id/analyze`, `POST /projects/:id/remove-background`, `POST /projects/:id/generate-prompt`, `POST /projects/:id/generate-creative`. Each step can return 202 + job id and poll `GET /jobs/:id`, or synchronously for quick steps.
- **Assets**: `GET /projects/:id/assets` or embedded in project; download via signed URL from Supabase Storage or via backend proxy.
- **Health**: `GET /health`.

### 0.4 Deliverables

- One-pager: user flows (anonymous, auth, dashboard, create-ad).
- Schema diagram or table list for Supabase (projects, assets, optional workflow_state).
- API endpoint list (method, path, auth, brief description).
- Simple wireframes or reference screens for: Landing, Sign up / Sign in, Forgot password, Dashboard (list + detail).

---

## Phase 1 — Database (Supabase) ✅ Done

**Objective**: Supabase project ready for auth, relational data, and file storage.

### 1.1 Supabase project

- Create project; note URL and anon/service keys.
- Enable Email auth (confirm email optional for MVP).
- Enable “Forgot password” (Supabase built-in: reset link to your frontend or hosted page).

### 1.2 Schema

- **`projects`**
  - `id` uuid PK default `gen_random_uuid()`
  - `user_id` uuid NOT NULL references `auth.users(id)` ON DELETE CASCADE
  - `name` text (nullable)
  - `status` text NOT NULL default `'draft'` (draft | analysing | processing | ready | failed)
  - `meta` jsonb (optional: product_name, target_audience, promotion_text, brand_positioning, etc.)
  - `created_at` timestamptz default `now()`
  - `updated_at` timestamptz default `now()`
- **`assets`**
  - `id` uuid PK default `gen_random_uuid()`
  - `project_id` uuid NOT NULL references `projects(id)` ON DELETE CASCADE
  - `type` text NOT NULL (original_upload | background_removed | cropped | final_creative)
  - `storage_path` text NOT NULL (bucket + path in Supabase Storage)
  - `mime_type` text
  - `created_at` timestamptz default `now()`
- **`workflow_state`** (optional)
  - `project_id` uuid PK references `projects(id)` ON DELETE CASCADE
  - `step` text, `payload` jsonb, `updated_at` timestamptz

### 1.3 Row Level Security (RLS)

- **`projects`**: `SELECT/INSERT/UPDATE/DELETE` where `auth.uid() = user_id`.
- **`assets`**: Same via `project_id` → join to `projects` and check `user_id`, or direct `project_id` in a policy that subqueries `projects`.
- **`workflow_state`**: Same as projects (only owner of project can read/write).

### 1.4 Storage

- Bucket(s): e.g. `project-assets` (private).
- Policy: allow read/write only for paths that correspond to the user’s projects (e.g. `user_id/project_id/filename`); enforce via RLS or backend-generated signed paths.

### 1.5 Deliverables

- Migrations (SQL) for tables + RLS + Storage policies.
- Env vars documented: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` (backend only).

---

## Phase 2 — Backend (in progress, part by part)

**Objective**: REST API that uses existing Python agents, reads/writes Supabase, and serves the frontend (and optionally Streamlit for internal use). Implemented in parts 2.1–2.7 (see Status overview).

### 2.1 Part 1 — Skeleton, CORS, auth ✅ Done

**What’s implemented**

- **FastAPI app** in `backend/main.py` with:
  - `GET /health` — public health check.
  - `GET /api/me` — protected route that returns the Supabase `user_id` from the JWT.
- **CORS** configured via `CORSMiddleware` using `CORS_ORIGINS` from `backend/config.py`.
- **Supabase client** (`backend/supabase_client.py`) using the **service role** key for server-side DB access.
- **JWT auth dependency** (`backend/auth.py`) that:
  - Reads the `Authorization: Bearer <supabase_access_token>` header.
  - Verifies the token with `SUPABASE_JWT_SECRET`.
  - Extracts and returns `sub` as the current `user_id`.

**How to test 2.1**

1. **Health**
   - Start the API (from `backend/`):
     - `uvicorn main:app --reload`
   - Open `http://localhost:8000/health`.
   - **Expected**: `{"status": "ok"}`.
2. **Auth wiring**
   - Sign in on the frontend (Supabase auth) and grab `session.access_token` (e.g. via `supabase.auth.getSession()` in the browser console).
   - Call `GET http://localhost:8000/api/me` with header:
     - `Authorization: Bearer <access_token>`.
   - **Expected**: `{"user_id": "<supabase_user_id>"}`.
   - If the token is missing/invalid, you should get a `401` with an error message.

### 2.2 Part 2 — Projects CRUD (next)

**Goal**

Expose basic project management endpoints that the frontend dashboard can call:

- `GET /api/projects` — list projects for the authenticated user.
- `POST /api/projects` — create a new project for the current user.
- `GET /api/projects/{id}` — get a single project by id (only if it belongs to the current user).

All routes:

- Require a valid Supabase JWT (reuse the existing auth dependency).
- Use the Supabase **service role** client for DB access.
- Respect the `projects` schema from Phase 1 (`user_id`, `status`, `meta`, timestamps).

**Testing strategy for 2.2 (once implemented)**

- From the browser or a tool like Postman:
  - Obtain a valid Supabase access token (same as for `/api/me`).
  - **Create**: `POST /api/projects` with JSON body (e.g. `{ "name": "Test project" }`) and auth header. Expect a 200/201 with a project object whose `user_id` matches your Supabase user id.
  - **List**: `GET /api/projects` with the same token. Expect to see the newly created project in the list, and not see projects from other users.
  - **Detail**: `GET /api/projects/{id}` with the project id. Expect the single project object; if you try an id that belongs to another user, expect a 404.

Implementation for 2.2 happens in `backend/main.py` (routes) using `get_supabase()` and `get_current_user_id`.

---

## Phase 3 — Frontend ✅ Done (shell)

**Objective**: Minimal, professional web app: Landing, Sign up/Sign in/Forgot password, Dashboard. Shell complete; project list/detail wiring and API integration follow as backend parts land.

### 3.1 Stack choice

- **Recommended**: Next.js (App Router) or Remix for SSR/SEO and simple deployment; or Vite + React if you prefer SPA-only.
- **Styling**: Tailwind with a tight design token set (2–3 colors, 2 font families, consistent spacing scale). Avoid default purple/blue gradients; pick a neutral or one accent that fits “meta ads / creative” (e.g. dark + one bold accent, or light + subtle borders).
- **Auth**: Supabase JS client (`@supabase/supabase-js`): `signUp`, `signInWithPassword`, `resetPasswordForEmail`; store session; protect dashboard routes.

### 3.2 Pages and features

- **Landing**
  - Hero: value prop (e.g. “Professional Meta ad creatives from your product images”).
  - Short “How it works” (3 steps).
  - Primary CTA: Sign up / Get started; secondary: Sign in.
  - Footer: minimal (links, legal if needed).
  - No heavy illustrations; optional one strong product image or simple graphic.

- **Sign up**
  - Email, password, optional confirm password.
  - Submit → Supabase `signUp` → redirect to dashboard or “check your email” if confirmation required.
  - Link to Sign in.

- **Sign in**
  - Email, password.
  - Submit → Supabase `signInWithPassword` → redirect to dashboard.
  - Links: Forgot password, Sign up.

- **Forgot password**
  - Email only → `resetPasswordForEmail` → “Check your email for reset link.”
  - Link back to Sign in.

- **Dashboard**
  - Header: Logo, nav (e.g. “Projects” or “Creatives”), user menu (Sign out).
  - Main: List of user’s projects (cards or table): name, status, date; click → project detail.
  - Project detail: Stepper or timeline (Upload → Analysis → BG remove → Prompt → Creative); actions per step (upload image, run analysis, run next step); preview of current asset and final creative when ready; download button.
  - Empty state: “Create your first ad” → starts new project (upload).

### 3.3 Design system (short)

- **Fonts**: One sans for UI (e.g. system stack or a single webfont like “DM Sans”, “Geist”, or “Outfit” — not Inter if you want to avoid default look).
- **Colors**: Background (e.g. white or off-white), text (near black), borders (light gray); one accent for primary buttons and links (e.g. deep orange or navy).
- **Spacing**: 4/8/16/24/32/48 px scale; sections with clear separation.
- **Components**: Buttons (primary, secondary, ghost), inputs, cards, status badges; no skeuomorphism.

### 3.4 State and API

- Use Supabase client for auth and, if desired, realtime project updates.
- REST API (Phase 2) for all workflow actions and asset URLs; fetch with `fetch` or axios, or React Query for cache and loading states.

### 3.5 Deliverables

- Next.js (or Vite) app with Landing, Auth (sign up, sign in, forgot password), Dashboard (list + project detail).
- Responsive layout; accessible forms and labels.
- Env: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_API_URL` (backend).

---

## Phase 4 — Integration, QA, Deploy

**Objective**: End-to-end flow working; deploy backend and frontend; minimal ops.

### 4.1 Integration

- E2E: One happy path (sign up → sign in → create project → upload → run through workflow → download creative) using Playwright or Cypress.
- Manual QA: Auth edge cases (wrong password, expired link), failed agent runs (show error in dashboard).

### 4.2 Deployment

- **Backend**: Docker on a VPS or PaaS (Railway, Render, Fly.io); env from secrets.
- **Frontend**: Vercel/Netlify (if Next/Vite) with env for Supabase and API URL.
- **Supabase**: Already hosted; ensure production URL and keys.

### 4.3 Observability

- Health check for API; optional logging (e.g. structured logs to stdout); error tracking (e.g. Sentry) for frontend and backend.

### 4.4 Deliverables

- E2E test(s) passing.
- Deploy docs or CI that build and run API + frontend.
- README update: how to run full stack (Supabase + API + frontend) for dev and prod.

---

## Phase Summary

| Phase | Focus           | Outcome                                              | Status   |
|-------|-----------------|------------------------------------------------------|----------|
| 0     | Discovery       | Flows, schema, API contract, wireframes              | Done     |
| 1     | Database        | Supabase: Auth, tables, RLS, Storage                  | Done     |
| 2     | Backend         | FastAPI REST API + existing agents + Supabase (parts 2.1–2.7) | In progress |
| 3     | Frontend        | Landing, Auth, Dashboard shell                       | Done     |
| 4     | Integration     | E2E, deploy, docs                                    | Pending  |

---

## Optional Later

- **Teams / workspaces**: Extra table `workspaces`, `workspace_members`; projects scoped to workspace.
- **Billing**: Stripe; usage or limits tied to `user_id` or workspace.
- **Realtime**: Supabase Realtime on `projects` so dashboard updates when status changes without polling.
- **Streamlit**: Keep as internal tool; same backend can be used by Streamlit for power users or support.

---

## Tech Summary

| Layer      | Choice                          |
|-----------|----------------------------------|
| Database  | Supabase (PostgreSQL, Auth, Storage) |
| Backend   | FastAPI (Python), Supabase client, existing agents |
| Frontend  | Next.js or Vite + React, Tailwind, Supabase JS |
| Auth      | Supabase Auth (email/password, forgot password) |
| Hosting   | API: Docker on VPS/PaaS; Frontend: Vercel/Netlify |

This roadmap is phase-wise and code-free; implementation starts only after you approve or adjust the plan.
