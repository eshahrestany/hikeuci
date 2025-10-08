# HikeUCI

HikeUCI is a monolithic, event-driven, full-stack web application designed to automate the weekly processes of the Hiking Club at UC Irvine.

This project provides:
- A public static site with general club info.
- Web forms for members to vote for trails, sign up for hikes, and electronically sign and submit waivers, based on a magic-link system.
- An admin dashboard for club officers to monitor and manage weekly hikes and statistics.
- Automated sending of templated emails via integration with UCI's official SMTP server.
---

## Tech Stack

| Layer      | Technology |
|------------|------------|
| **Back-end** | [Flask](https://flask.palletsprojects.com/) · [SQLAlchemy](https://www.sqlalchemy.org/) · [Alembic/Flask-Migrate](https://alembic.sqlalchemy.org/en/latest/) |
| **Database** | [PostgreSQL](https://www.postgresql.org/) |
| **Task Queue** | [Celery](https://docs.celeryq.dev/en/stable/) · [Redis](https://redis.io/) |
| **Front-end** | [Vue 3](https://vuejs.org/) · [Vite](https://vite.dev/) · [Tailwind CSS](https://tailwindcss.com/) |
| **Deployment** | [Docker](https://www.docker.com/) · [Coolify](https://coolify.io) |

---

## Repository Layout
Not all files in the repo are shown here, this is just the basic layout.

```text
hikeuci/
├─ backend/
│  ├─ .env                    # Backend environment variables
│  ├─ app/                    # Flask application
│  │  ├─ models.py            # Database class-based models (Uses SQLAlchemy)
│  │  ├─ routes/              # REST API endpoints (organized with Blueprints)
│  │  ├─ lib/                 # Helper functions organized by file
│  │  └─ extensions.py        # Flask extensions (db, migrate, celery)
│  ├─ migrations/             # Alembic migration history
│  ├─ static/                 # Where uploaded trail images are stored
│  ├─ templates/              # Template file location (emails, waiver content)
│  ├─ config.py               # Object-oriented Flask config declaration which reads from environment variables
│  ├─ devtools.py             # Scripts for seeding the database with example data/scenarios
│  ├─ manage.py               # WSGI entry-point / dev server
│  ├─ make_celery.py          # Celery/Beat app bootstrap
│  └─ requirements.txt        # Python dependencies
│
├─ frontend/
│  ├─ .env                    # Frontend environment variables
│  ├─ src/                    # Root directory for all frontend source code
│  │  ├─ assets/              # Frontend static asset files
│  │  ├─ components/          # Reusable Vue components
│  │  │  ├─ public/           # Components which are used in the public pages
│  │  │  ├─ admin/            # Components which are used in the admin dashboard
│  │  │  ├─ common/           # Components used in both
│  │  │  ├─ ui/               # shadcn-vue files. This folder's content is auto-populated by npx scripts
│  │  ├─ views/               # Full-page vue components which correspond to a webpage
│  │  │  ├─ public/           # public pages
│  │  │  ├─ admin/            # dashboard pages
│  │  ├─ lib/                 # JS helpers
│  │  ├─ router/              # The Vue router to configure frontend routing
│  │  ├─ App.vue              # The root component which contains the router view
│  ├─ package.json            # Node dependencies
│  └─ vite.config.ts          # Vite configuration
```

---

## How does it all work?

This description will hopefully give a general idea of what happens in the webapp during our weekly hike campaigns.

A *campaign* (the word i've unofficially dubbed as the entire process of organizing a hike which I am about to describe)
begins with an officer pressing the "Set Next Hike" button on the dashboard, typically on a Sunday or Monday.
A hike campaign has three phases: `Voting`, `Signup`, and `Waiver`.

When setting the hike, the officer sets timestamps for the events-- namely:
1. the date/time when voting closes and signups are sent out (typically Tuesday at 6pm)
2. the date/time when signups close and waivers are sent out (typically Thursday at 6pm)
3. the date/time of the hike (typically Saturday at 8am). waivers don't close until a little after-- more on that later.

The officer also has the option of skipping the voting phase and picking the trail for the week.
Otherwise, the officer picks three trail options and begins the campaign. 

A row is added to the `hikes` table with the status set to `active` and the phase set to `voting` (or `signup` if skipped).
Immediately, an email campaign begins. Magic links tied to the new hike are generated for every member in the club, and 
a voting email is personalized from a template with information specific to both the new hike (in the case of vote emails,
that's just the trail options) and the magic link, specific to each user. 

Emails are sent to every user one by one via an SMTP server,
performed asynchronously from the rest of the flask app as this process is handled by a Celery worker.

Magic links point to the public site, and contain a token which is specific to a user and a phase of a hike. They expire 
at the end of a hike phase. During the voting phase, the magic links allow users to vote for a trail, and with the same 
link they can return to the public site and change their vote at any time before expiry.

How does voting for a trail work? The member submits a POST request from the voting webpage to /api/vote with
the token in the request payload. The server will look up the token, and if valid, create a new row in the `votes` table
for the associated member or update an existing one if the member is changing a vote.

Once a minute at the start of every minute, a Celery Beat worker enqueues a task. That task reads the `hikes` table,
and looks for active hikes. If the current system time has passed the timestamp specified to move on to the next phase,
the task initiates a script which initiates the next phase of the hike. When going from `voting` to `signup`,
for example, the script will count the trail votes, set the trail_id on the hike table row to the winning trail,
update the phase to `signup`, and initiate a signup email campaign.

The process for the signup phase is much the same, this time members create a row in the `signups` table with their
signup info, and the `status` column set to `pending`. Drivers can create rows in the `vehicles` table from this form and
specify its passenger capacity, and their signup row will point to the vehicle they have chosen to drive with.

At the end of the signup phase, the minutely update task once again initiates a phase script. The `initiate_waiver_phase`
script runs the selection algorithm to determine who gets to hike and who is waitlisted, based on the total capacity
calculated from all driver signups. It then updates the `signups` table for all signups with the `status` column to either
`confirmed`, or `waitlisted` + the `waitlist_pos`.

Emails are then sent out to all selected members with a magic link to sign a waiver, and waitlisted members receive
an email letting them know their position on the waitlist.

Members fill and sign a templated form with information pertaining to this week's hike. When POSTing a completed waiver,
the server will create a row in the `waivers` table for the associated member and hike. Signatures are stored as base64
image data.

On the morning of the hike, officers check people in for attendance. This is just a simple button in the dashboard
that marks the member's `signup` row with the boolean `is_checked_in`.

There is a server config for specifying the number of hours after the aforementioned hike timestamp when the hike will
be internally marked as completed. After this point, we reach the end of a hike campaign and the update task changes 
the `phase` of the hike from `waiver` to `NULL` and the  `status` from `active` to `past`.

This wraps up the process of a hike campaign. I'm glossing over lots of details, but anyone who wishes to find out more
details can search through the code for specifics.

# Development Guide

## Preface

This is a complex application, and doing development requires knowledge about full-stack development, familiarity with 
the frameworks involved in the project, and a general understanding of how web apps run in development, production, 
and the differences between the environments.

Before diving into how to set up the project, let's talk a little bit about what this app looks like in deployment. 
It will make sense why later.

Firstly, Hiking Club pays for A VPS running Debian Linux. On it, we run an instance of Coolify. Through the Coolify 
dashboard, we configure and deploy six Docker containers:
1. A PostgreSQL server (publicly available Docker image)
2. Redis (^ same deal)
3. Backend container (backend/Dockerfile): serves the Flask app using Gunicorn (production WSGI server).
4. Celery workers (backend/Dockerfile-celery): Run asynchronous tasks like sending emails and scheduled tasks.
5. Celery-beat (backend/Dockerfile-celery-beat): Initiates tasks on a regular interval
6. Frontend container (frontend/Dockerfile): servers the SPA built with Vite using NGINX

As evident from the repository layout, this project is primarily split into *backend* (Flask) and *frontend* (Vue).
It is **highly** recommended to develop in Linux or macOS. Use WSL if you are on windows, as Celery does not natively support Windows.
For your IDE-- VS Code is nice for small projects, but I would recommend Pycharm professional edition for this project. 
[It's free for students](https://www.jetbrains.com/academy/student-pack/), it handles a lot of the environment setup for you, and it has a lot of tools that VS Code
lacks for full-stack webapp development. I will continue the setup tutorial specific to PyCharm.

## 0. Prerequisites

* **Node.js 22** - get with NVM
* **Docker Desktop**, then get and run the following two images from the Docker Hub
  * **PostgreSQL** database
  * **Redis** (for Celery broker/result backend)

## 1. Project Setup

Fork the repo on GitHub first. Then, create a new project from PyCharm, and select your forked repo. Set up a python
virtualenv (on WSL if on windows) for the latest version of `3.12`. 

In the top right corner of PyCharm, click Database, click New > Data Source > PostgreSQL. Fill in the connection details
from the Docker container. Download missing driver files if prompted. You will be able to access and modify the database
from within PyCharm in this panel.


## 2. Set up a Google Cloud app
To set up signing in with Google for your local dev environment. you'll need to access the [Google Cloud Console](https://console.cloud.google.com).
Create a project, and set up OAuth in that project.

Add `http://127.0.0.1:5001` to *Authorized Javascript Origins*.
Add `http://127.0.0.1/api/admin/authorize` to *Authorized Redirect URIs*.

Copy the Client ID and the Client Secret, and paste them into your .env; more info on that below.
(once you copy the client secret you can't access it again! don't lose it!)


## 3. Configure environment variables

There are two .env files for this project: backend/.env (the main one) and frontend/.env (contains just the Google Client ID 
for Google OAuth, which is a public ID).

#### Backend
Create a file called `.env` in `backend/` with at least the following. 
Values shown are examples for local development; adjust for your environment. The Postgres and Redis values are default
from the docker container in docker desktop, make sure you are exposing the ports 5432 and 6379 for postgres and redis respectively.

The dummy email mode is good for development, but if you have a SMTP server you can do testing with, even better. Set DUMMY_EMAIL_MODE
to false and input the connection details to your server.

For beginner developers: NEVER commit your .env!!! Or any file with secret tokens (although you should always just keep them in your .env anyway)!!!

The JWT secret can be any random string of characters, it doesn't matter in development.


```env
# Required: Database (PostgreSQL)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=hikeuci
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

# Required: CORS and JWT (used by admin dashboard auth)
CORS_ORIGIN=http://127.0.0.1:5001
JWT_SECRET_KEY=[change-me]
JWT_ALGORITHM=HS256
JWT_EXP_HOURS=8

# Required: Flask Params
FLASK_APP=manage.py
FLASK_ENV=development
BASE_URL=http://localhost:5001

# Required: Google Sign-In (admin login)
GOOGLE_CLIENT_ID=[your-google-oauth-client-id]
GOOGLE_CLIENT_SECRET=[your-google-client-secret]
GOOGLE_TOKEN_INFO_URL=https://oauth2.googleapis.com/tokeninfo

DUMMY_EMAIL_MODE=true

# Celery / Redis
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

# Optional email tuning
MAIL_FROM=hiking@example.com
MAIL_BATCH_SIZE=100
MAIL_MAX_ATTEMPTS=3
MAIL_BATCH_PAUSE_SEC=5

DUMMY_EMAIL_MODE=true
# Optional SMTP setup
# MAIL_SMTP_HOST=your-host.com
# MAIL_SMTP_PORT=587
# MAIL_SMTP_USERNAME=username
# MAIL_SMTP_PASSWORD=password
# MAIL_SMTP_TIMEOUT=30

# Server behavior variables
HIKE_RESET_TIME_HR=6
SERVER_TIMEZONE=America/Los_Angeles
```
#### Frontend

Create `frontend/.env` and set:

```env
VITE_GOOGLE_CLIENT_ID=[your-google-oauth-client-id]
```

This is consumed in the Sign-In view via `import.meta.env.VITE_GOOGLE_CLIENT_ID`.

Remember to replace all values in [brackets].

## 4. First-time setup commands

Befriend the terminal panel at the bottom, you'll use it for everything but editing files. I often find myself using
5+ terminal tabs open during development.

Opening a new terminal window should automatically activate the venv (note the (.venv) in the beginning of the CL).

In the terminal, `cd backend`. Then, from /backend, 
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize database (creates all tables) with alembic:
```bash
flask --app backend/manage.py db upgrade
```

3. Start the Flask dev server (api runs at http://127.0.0.1:5000):
```bash
flask run --debug 
```

Your API is now running via Flask, with hot reloading thanks to --debug 
(changes you make to routes will have immediate effect the next time that route is called).

4. Make a new terminal tab and run:
```bash
cd frontend
npm install     # install all packages from package.json
npm run dev     # Vite dev server at http://127.0.0.1:5001
```
Your frontend is now running, and you can access the website from your browser.

The dev server proxies all requests beginning with `/api` to `http://127.0.0.1:5000` (see `frontend/vite.config.ts`).


## Seeding the database
For now, our Postgres server is empty. Let's start by adding ourselves as an admin user so we can access
the officer dashboard. In the PyCharm database panel, find the admin_users table and create a new row. 
Set `provider` to `google`, type in your email, and set the created_on to now (double click). You should be able to
sign in to the dashboard with the google login.

The file `backend/devtools.py` contains a number of scripts which fill the database with example data representing 
example scenarios (a hike in the signup phase with example members signed up already, etc.).
Running any of these scripts clears the database before repopulating it with example data, and are therefore never
to be run in production (obviously).

Populate your database with a hike in the waiver phase by running
`python3 devtools.py waiver`.
It takes a system argument to specify the scenario. Read through the file to see the other scenarios
and learn what they do, or, if you ever find it convenient for development, make a scenario of your own.

Once the waiver phase is seeded, hit `Refresh data` on the dashboard. You should see the example data displayed.
## Doing development
You should now have everything you need to begin doing work. The reason I mentioned the production setup earlier was to
give an idea of how many concurrent processes need to be running for the entire app to run, however,
not all of those processes are always needed to be up in development. For example, Celery workers need to be run to 
test email sending, and with dummy email mode enabled, the email content will be simply logged to the worker output.
If the development you are doing doesn't have anything to do with emails (or the phase-change scripts), then you most 
likely won't need to run celery. Most of the time, just hosting the frontend and backend are enough. 

### Shadcn
When doing frontend development, specifically for the dashboard, browse the components available from 
[shadcn-vue](https://www.shadcn-vue.com/).
If you find any components that are useful for your situation, add them with the npx command and import them in
the Vue component you want to add them to. The folder `backend/components/ui` will be auto populated with 
premade shadcn-vue component(s). Be sure to commit these new files.


---

## Useful Commands reference

| Task | Command                                                   |
|------|-----------------------------------------------------------|
| Seed sample data (from repo root) | `python3 backend/devtools.py signup`                      |
| Generate a new migration | `flask --app backend/manage.py db migrate -m "message"`   |
| Apply migrations | `flask --app backend/manage.py db upgrade`                |
| Front-end dev server | `npm run dev` (in `frontend/`)                            |
| Production build of SPA | `npm run build` (in `frontend/`)                          |
| Celery worker | `celery -A backend.make_celery.celery_app worker -l info` |
| Celery beat | `celery -A backend.make_celery.celery_app beat`           |

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

# Workflow, and things to remember

1. Fork and branch from the latest default branch.
   - Suggested branch names: `feature/<name>`, `fix/<issue>`, `chore/<task>`
2. Do the work and write clear commits (Conventional Commits are appreciated):
   - Examples: `feat(admin): add waitlist table`, `fix(api): handle missing token`, `chore: bump deps`
3. Push your branch and open a pull request.
   - Include a summary of changes, screenshots for UI changes, and manual test steps.

### Database changes

- Include Alembic migration files under `backend/migrations/versions/` for any schema change
- Do not modify existing migrations; always create a new one

### Style and conventions

- Python: prefer readable code, type hints for public functions, early returns, and meaningful names
- Vue/JS: keep components small, colocate logic, and prefer explicit props/emits
- Commit messages: use present tense; scope with `feat`, `fix`, `docs`, `chore`, etc.


## Questions?
Try to figure it out on your own first. I find that's a great way to learn. Also try asking ChatGPT; if you give it
the right context its usually great at explaining things.

If you still cant figure something out and Chat is hallucinating, ping @pgq in the
[Hiking Club discord server](https://discord.com/invite/jWcN8dWQzC).

## License

This project is licensed under the MIT License. See `LICENSE` for details. 

