# HikeUCI

HikeUCI is a full-stack web application for the UC Irvine Hiking Club.
It provides a small REST API for managing members, trails, and hikes
alongside a modern Vue 3 front-end that consumes the API.

---

## Tech Stack

| Layer      | Technology |
|------------|------------|
| **Back-end** | [Flask](https://flask.palletsprojects.com/) · SQLAlchemy · Alembic/Flask-Migrate |
| **Database** | PostgreSQL |
| **Task Queue** | Celery · Redis |
| **Front-end** | [Vue 3](https://vuejs.org/) · Vite · Tailwind CSS |

---

## Repository Layout

```text
hikeuci/
├─ backend/                   # Flask application
│  ├─ app/                    # Application package
│  │  ├─ models.py            # SQLAlchemy models
│  │  ├─ routes/              # Blueprints (REST endpoints)
│  │  └─ extensions.py        # Flask extensions (db, migrate, celery)
│  ├─ migrations/             # Alembic migration history
│  ├─ manage.py               # WSGI entry-point / dev server
│  ├─ make_celery.py          # Celery/Beat app bootstrap
│  └─ requirements.txt        # Python dependencies
│
├─ frontend/                  # Vue 3 single-page app
│  ├─ src/                    # Vue components, router, assets
│  └─ vite.config.ts          # Dev server + proxy configuration
│
└─ README.md                  # You are here 🗺️
```

---

## Getting Started

The project is split into *backend* (Python) and *frontend* (Node). You can
run them side-by-side during development.

### 0. Prerequisites

* **Python ≥3.9**
* **Node.js ≥22**
* **PostgreSQL** database
* **Redis** (for Celery broker/result backend)

### 1. Clone the repository

```bash
git clone https://github.com/your-user/hikeuci.git
cd hikeuci
```

### 2. Configure environment variables

Create a file called `.env` in `backend/` with at least the following. Values shown are examples for local development; adjust for your environment.

```env
# Required: Database (PostgreSQL)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=hikeuci
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

# Required: CORS and JWT (used by admin dashboard auth)
CORS_ORIGIN=http://127.0.0.1:5001
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_EXP_HOURS=8

# Required: Flask Params
FLASK_APP=manage.py
FLASK_ENV=development
BASE_URL=http://localhost:5001

# Required: Google Sign-In (admin login)
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_TOKEN_INFO_URL=https://oauth2.googleapis.com/tokeninfo

# Required in development to disable real emails
DUMMY_EMAIL_MODE=true
MAIL_FROM=hiking@example.com

# Celery / Redis
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

# Optional email tuning (defaults shown)
MAIL_BATCH_SIZE=100
MAIL_MAX_ATTEMPTS=3
MAIL_BATCH_PAUSE_SEC=5

# Optional SMTP setup
MAIL_SMTP_HOST=your-host.com
MAIL_SMTP_PORT=587
MAIL_SMTP_USERNAME=username
MAIL_SMTP_PASSWORD=password
MAIL_SMTP_TIMEOUT=30

# Optional server behavior
HIKE_RESET_TIME_HR=6
SERVER_TIMEZONE=America/Los_Angeles
```

### 3. Back-end setup

```bash
# From the repository root

# Create & activate a virtualenv
python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate    # macOS / Linux

# Install Python deps
pip install -r backend/requirements.txt

# Initialize database (creates all tables)
flask --app backend/manage.py db upgrade

# Start the Flask dev server (http://127.0.0.1:5000)
python backend/manage.py
```

In a separate terminal, start the background workers:

```bash
# Celery worker
celery -A backend.make_celery.celery_app worker --loglevel=info

# Celery beat (schedules phase progression checks)
celery -A backend.make_celery.celery_app beat --loglevel=info
```

### 4. Front-end setup

```bash
cd frontend
npm install
npm run dev     # Vite dev server at http://127.0.0.1:5001
```

The dev server proxies all requests beginning with `/api` to `http://127.0.0.1:5000` (see `frontend/vite.config.ts`).

---

## Useful Commands

| Task | Command |
|------|---------|
| Seed sample data (from repo root) | `python backend/devtools.py signup` |
| Generate a new migration | `flask --app backend/manage.py db migrate -m "message"` |
| Apply migrations | `flask --app backend/manage.py db upgrade` |
| Front-end dev server | `npm run dev` (in `frontend/`) |
| Production build of SPA | `npm run build` (in `frontend/`) |
| Celery worker | `celery -A backend.make_celery.celery_app worker` |
| Celery beat | `celery -A backend.make_celery.celery_app beat` |

---

## API Quick Peek

All endpoints are prefixed with `/api`.

- Auth (admin login)
  - `POST /api/auth/google` — exchanges Google ID token for a JWT.
- Admin dashboard
  - `GET /api/admin/upcoming` — active hike status/timeline.
  - `POST /api/admin/set-hike` — create next hike (vote or signup flow).
  - `GET /api/admin/waitlist` — list waitlisted users (waiver phase only).
  - `GET /api/admin/list-emails-not-in-hike` — helper list for email campaign.
  - `POST /api/admin/check-in` — mark user checked-in (waiver phase).
  - `POST /api/admin/modify-user` — edit user and transport type.
  - `POST /api/admin/remove-user` — remove user from current hike.
  - `POST /api/admin/add-user` — add user to current hike.
- Trails
  - `GET /api/trails` — list trails (admin auth required).
- Vehicles
  - `GET /api/vehicles?member_id=…` — list member vehicles (admin auth).
  - `POST /api/vehicles` — create a vehicle (admin auth).
- Images
  - `GET /api/images/uploads/{trail_id}.png` — serve trail image.
- Mail
  - `POST /api/mail/resend` — enqueue resend of an email (admin auth).
- Magic link flows (emails sent by Celery)
  - `GET/POST /api/hike-vote?token=…` — voting page data / submit vote.
  - `GET/POST /api/hike-signup?token=…` — signup page data / submit form.
  - `GET/POST /api/hike-signup/cancel?token=…` — cancel signup.
  - `GET/POST /api/hike-waiver?token=…` — waiver page data / submit waiver.
  - `POST /api/hike-waiver/cancel?token=…` — cancel signup during waiver phase.

---

## Deployment

You can deploy with Docker using the provided Dockerfiles, or run the components directly.

### Docker: Backend (Gunicorn)

`backend/Dockerfile` builds a Flask image that installs `backend/requirements.txt` and starts Gunicorn:

```bash
# From repo root
docker build -t hikeuci-backend ./backend

# Ensure your database and redis are reachable from the container
# Expose backend on 8000 (see nginx upstream)
docker run --env-file backend/.env \
  -p 8000:8000 \
  --name hikeuci-backend \
  hikeuci-backend
```

Notes:
- The Dockerfile ends with Gunicorn launching the app; ensure env vars are provided via `--env-file`.
- It also runs a `flask db upgrade` as an earlier CMD. If overriding the command, run migrations separately.

### Docker: Celery worker and beat

```bash
docker build -t hikeuci-celery ./backend -f backend/Dockerfile-celery
docker run --env-file backend/.env --name hikeuci-celery hikeuci-celery

docker build -t hikeuci-celery-beat ./backend -f backend/Dockerfile-celery-beat
docker run --env-file backend/.env --name hikeuci-celery-beat hikeuci-celery-beat
```

Ensure `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` point to a reachable Redis instance.

### Docker: Nginx + SPA

`nginx/Dockerfile` builds the Vue app (Node 22) and serves it via Nginx, proxying `/api` to the backend:

```bash
# Build the nginx image (also builds the Vue SPA)
docker build -t hikeuci-nginx ./ -f nginx/Dockerfile

# Run, mapping port 80 on the host
docker run -p 80:80 --name hikeuci-nginx hikeuci-nginx
```

The Nginx config at `nginx/nginx.conf` proxies `/api` to `backend:8000`. When using Docker Compose or a multi-container setup, set the Gunicorn container name (or service name) to `backend` and expose it on port `8000` to match.

### Bare-metal (non-Docker)

1. Build the SPA: run `npm run build` in `frontend/` (outputs to `frontend/dist/`).
2. Serve the built assets with a web server (e.g., Nginx). This repo does not include a Flask route to serve `index.html`; Flask only serves the API.
3. Run Gunicorn, e.g.: `gunicorn -w 4 -k gevent -b 0.0.0.0:5000 backend.manage:app`
4. Run Celery worker(s) and beat alongside the web app.
5. Put everything behind a reverse proxy (e.g., Nginx, Traefik).

---

## Contributing

Contributions are welcome! Please use short, descriptive PRs and keep changes scoped.

### Workflow

1. Fork and branch from the latest default branch.
   - Suggested branch names: `feature/<name>`, `fix/<issue>`, `chore/<task>`
2. Do the work and write clear commits (Conventional Commits are appreciated):
   - Examples: `feat(admin): add waitlist table`, `fix(api): handle missing token`, `chore: bump deps`
3. Push your branch and open a pull request.
   - Include a summary of changes, screenshots for UI changes, and manual test steps.

### PR checklist (no CI yet)

There is currently no CI configured. Please self‑verify before requesting review:

- Backend
  - Flask dev server starts: `python backend/manage.py`
  - Database migrations created and applied: `flask --app backend/manage.py db migrate -m "msg" && flask --app backend/manage.py db upgrade`
  - Celery worker and beat start: `celery -A backend.make_celery.celery_app worker` and `... beat`
- Frontend
  - Dev server runs: `cd frontend && npm run dev`
  - Production build passes: `npm run build`
- Docs
  - Updated `README.md` for any new env vars, commands, or endpoints
- Optional
  - Run a local smoke test using `python backend/devtools.py signup` to seed data

### Database changes

- Include Alembic migration files under `backend/migrations/versions/` for any schema change
- Do not modify existing migrations; always create a new one

### Style and conventions

- Python: prefer readable code, type hints for public functions, early returns, and meaningful names
- Vue/JS: keep components small, colocate logic, and prefer explicit props/emits
- Commit messages: use present tense; scope with `feat`, `fix`, `docs`, `chore`, etc.

### Security and secrets

- Do not commit secrets. Use `backend/.env` locally and document new env vars in this file
- If adding new secrets, note whether they are required for local development

---

## License

This project is licensed under the MIT License. See `LICENSE` for details. 
