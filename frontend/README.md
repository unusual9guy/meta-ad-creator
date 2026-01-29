# Meta Ad Creator — Frontend

Minimal, professional web app for the Meta Ad Creator: landing, auth (sign up / sign in / forgot password), and dashboard.

## Stack

- **Next.js 14** (App Router)
- **Tailwind CSS** (design tokens: brand, surface, ink)
- **Supabase** (auth via `@supabase/supabase-js`)
- **Font**: Outfit (Google Fonts)

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy env example and set Supabase keys:
   ```bash
   cp .env.local.example .env.local
   ```
   Edit `.env.local` and set:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`

3. Run dev server:
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000).

## Pages

- **/** — Landing (hero, how it works, CTAs)
- **/sign-up** — Create account
- **/sign-in** — Sign in
- **/forgot-password** — Reset password
- **/dashboard** — Projects list (empty state until backend)
- **/dashboard/new** — New project (placeholder)
- **/dashboard/projects/[id]** — Project detail (placeholder)

## Backend

Workflow and project data will be wired when the Phase 2 API is ready. Set `NEXT_PUBLIC_API_URL` in `.env.local` when available.
