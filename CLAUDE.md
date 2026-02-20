# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Frontend (run from `frontend/`)
```bash
npm install                # install dependencies
npm run dev                # Vite dev server at http://127.0.0.1:5001
npm run build              # production build to dist/
```

### Backend (run from repo root)
```bash
pip install -r backend/requirements.txt           # install dependencies
flask --app backend/manage.py run --debug          # Flask dev server at http://127.0.0.1:5000
flask --app backend/manage.py db upgrade           # apply migrations
flask --app backend/manage.py db migrate -m "msg"  # generate new migration
```

### Celery (run from repo root, needed for email sending and phase transitions)
```bash
celery -A backend.make_celery.celery_app worker -l info   # async task worker
celery -A backend.make_celery.celery_app beat              # scheduled task runner
```

### Database Seeding (run from repo root)
```bash
python3 backend/devtools.py voting   # seed DB with voting-phase scenario
python3 backend/devtools.py signup   # seed DB with signup-phase scenario
python3 backend/devtools.py waiver   # seed DB with waiver-phase scenario
```
Warning: seeding clears the entire database before repopulating.

### Adding shadcn-vue Components
```bash
npx shadcn-vue@latest add <component>   # auto-populates frontend/src/components/ui/
```

## Architecture

HikeUCI is a full-stack web app for managing weekly hiking club events at UC Irvine. Monorepo with a Flask API backend and Vue 3 SPA frontend.

### Three-Phase Hike Campaign

The core domain revolves around a weekly hike "campaign" with three sequential phases:

1. **Voting** - Members receive magic-link emails and vote for 1 of 3 trail options
2. **Signup** - Members sign up with transport preference (driver/passenger/self)
3. **Waiver** - A selection algorithm runs based on driver capacity, confirming or waitlisting members. Confirmed members sign waivers electronically.

Phase transitions are driven by timestamps set when creating a hike. A Celery Beat task (`check_and_update_phase`) runs every minute to check if it's time to advance phases. Each transition triggers an email campaign via Celery workers.

### Magic Link System

Public flows (voting, signup, waiver) require no user accounts. Instead, personalized magic-link tokens are generated per member per hike phase. Tokens are validated in `backend/app/lib/magic_link.py` against hike status/phase and expire when the phase ends.

### Backend Structure

- **`backend/app/__init__.py`** - Flask app factory (`create_app`)
- **`backend/app/models.py`** - All SQLAlchemy models (Member, Trail, Hike, Signup, Waiver, Vehicle, Vote, MagicLink, AdminUser, EmailCampaign, EmailTask)
- **`backend/app/routes/`** - Flask Blueprints organized by feature (auth, dashboard, vote, signup, waiver, trails, members, vehicles, mail, images, dashboard_history)
- **`backend/app/lib/`** - Business logic helpers (magic links, phase transitions, selection algorithm, email sending, PDF generation)
- **`backend/app/decorators.py`** - `@admin_required` (JWT validation), `@waiver_phase_required`
- **`backend/app/extensions.py`** - Shared Flask extensions (db, migrate, celery)
- **`backend/manage.py`** - WSGI entry point
- **`backend/make_celery.py`** - Celery app bootstrap
- **`backend/migrations/`** - Alembic migration history (never modify existing migrations, always create new ones)

### Frontend Structure

- **`frontend/src/router/index.js`** - Vue Router config with public and admin route groups
- **`frontend/src/views/public/`** - Public pages (Index, SignIn, Vote, Signup, Waiver)
- **`frontend/src/views/admin/`** - Dashboard pages (DashboardLayout, Dashboard, DashboardTrails, DashboardMembers, HikeHistory)
- **`frontend/src/components/public/`** - Public-facing components
- **`frontend/src/components/admin/`** - Admin dashboard components
- **`frontend/src/components/common/`** - Shared components
- **`frontend/src/components/ui/`** - Auto-generated shadcn-vue components (do not manually edit)
- **`frontend/src/lib/auth.js`** - Composition API auth store with JWT management and fetch helpers
- **`@` alias** resolves to `frontend/src/` (configured in vite.config.ts)

### Auth

Admin authentication uses Google OAuth 2.0. The backend exchanges Google ID tokens for JWTs (`POST /api/auth/google`). The `@admin_required` decorator validates JWTs on all admin endpoints. Frontend stores tokens in localStorage and auto-signs out on 401.

### API

All endpoints are prefixed with `/api`. The Vite dev server proxies `/api` requests to `http://127.0.0.1:5000`. Public magic-link endpoints accept tokens as query parameters.

### Dev Environment

Requires PostgreSQL and Redis running (via Docker). Frontend on port 5001, backend on port 5000. Set `DUMMY_EMAIL_MODE=true` in `backend/.env` to log emails to Celery worker output instead of sending via SMTP.

## Conventions

- **Python**: Type hints for public functions, early returns, meaningful names
- **Vue**: Composition API with `<script setup>`, small focused components, explicit props/emits
- **Commits**: Conventional commits - `feat(scope): message`, `fix(scope): message`, `chore: message`
- **Branches**: `feature/<name>`, `fix/<issue>`, `chore/<task>`
- **Styling**: Tailwind CSS 4.0 utility classes, dark mode supported
