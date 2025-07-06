# HikeUCI

HikeUCI is a full-stack web application for the UC Irvine Hiking Club.
It provides a small REST API for managing members, trails, and hikes
alongside a modern Vue 3 front-end that consumes the API.

---

## Tech Stack

| Layer      | Technology |
|------------|------------|
| **Back-end** | [Flask](https://flask.palletsprojects.com/) · SQLAlchemy · Alembic/Flask-Migrate |
| **Database** | PostgreSQL (⇢ any SQLAlchemy-compatible DB – SQLite works for local development) |
| **Front-end** | [Vue 3](https://vuejs.org/) · Vite · Tailwind CSS |

---

## Repository Layout

```text
hikeuci/
├─ backend/              # Flask application
│  ├─ app/               # Application package
│  │  ├─ models.py       # SQLAlchemy models
│  │  ├─ routes/         # Blueprints (REST endpoints)
│  │  └─ extensions.py   # Flask extensions (db, migrate)
│  ├─ migrations/        # Alembic migration history
│  └─ manage.py          # WSGI entry-point / dev server
│
├─ frontend/             # Vue 3 single-page app
│  ├─ src/               # Vue components, router, assets
│  └─ vite.config.js     # Proxy / build configuration
│
├─ requirements.txt      # Python dependencies
└─ README.md             # You are here 🗺️
```

---

## Getting Started

The project is split into *backend* (Python) and *frontend* (Node). You can
run them side-by-side during development.

### 0. Prerequisites

* **Python ≥3.9**
* **Node.js ≥18** (comes with `npm` ≥9)
* A SQL database. For quick local testing you can use SQLite; for real usage
  we recommend PostgreSQL.

### 1. Clone the repository

```bash
git clone https://github.com/your-user/hikeuci.git
cd hikeuci
```

### 2. Configure environment variables

Create a file called `.env` at the project root (or inside `backend/`) and set
`DATABASE_URL`. Two common examples are shown below:

```env
# SQLite – great for local hacking
DATABASE_URL=sqlite:///hikeuci.db

# PostgreSQL – replace with your own connection parameters
# DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/hikeuci
```

### 3. Back-end setup

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
# python -m venv .venv
# source .venv/bin/activate

pip install -r requirements.txt

# Run database migrations (creates all tables)
flask --app backend/manage.py db upgrade

# Start the dev server on http://localhost:5000
python backend/manage.py
```

### 4. Front-end setup

```bash
cd frontend
npm install     # installs Vue, Vite, Tailwind, …
npm run dev     # launches Vite dev server on http://localhost:5173
```

`vite.config.js` is configured to **proxy** every request beginning with
`/api` to `http://localhost:5000`, so the SPA can seamlessly talk to the Flask
API during development.

---

## Useful Commands

| Task | Command |
|------|---------|
| Run unit tests *(if/when added)* | `pytest` |
| Auto-format Python code | `ruff format .` |
| Generate a new migration | `flask --app backend/manage.py db migrate -m "message"` |
| Apply migrations | `flask --app backend/manage.py db upgrade` |
| Production build of SPA | `npm run build` |

---

## API Quick Peek

A small example endpoint is provided at `/api/example`.

```bash
curl http://localhost:5000/api/example/
# → {"message": "Hello World"}
```

`/api/example/upcoming` returns the next upcoming hike if one exists.
Extend the blueprints in `backend/app/routes/` to add more functionality.

---

## Deployment

For production you will likely:

1. Build the front-end: `npm run build` → serves static files from `frontend/dist/`.
2. Configure a WSGI server (e.g. **Gunicorn** or **uWSGI**) to run
   `backend/manage.py`.
3. Put everything behind a reverse proxy like **Nginx** or **Caddy**.

Dockerfiles / CI pipelines are left to the reader for now – PRs welcome!

---

## Contributing

1. Fork the repo & create your branch: `git checkout ‑b feature/awesome`.
2. Commit your changes: `git commit -m 'Add awesome feature'`.
3. Push to the branch: `git push origin feature/awesome`.
4. Open a pull request.

Please follow conventional commit messages and ensure the
CI (formatters, linters, tests) passes.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details. 