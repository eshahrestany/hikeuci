import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    BASE_URL = os.getenv("BASE_URL")
    user = os.getenv("POSTGRES_USER")
    pw = os.getenv("POSTGRES_PASSWORD")
    dbn = os.getenv("POSTGRES_DB")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{user}:{pw}@{host}:{port}/{dbn}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    JWT_EXP_HOURS = os.getenv("JWT_EXP_HOURS")

    CORS_ORIGIN = os.getenv("CORS_ORIGIN")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_TOKEN_INFO_URL = os.getenv("GOOGLE_TOKEN_INFO_URL")

    CELERY = {
        "broker_url": os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        "result_backend": os.getenv("CELERY_RESULT_BACKEND")
    }

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    FRONTEND_DIST = os.path.join(BASE_DIR, '..', 'frontend', 'dist')
    STATIC_FOLDER = os.path.join(FRONTEND_DIST, 'assets')
    TEMPLATE_FOLDER = FRONTEND_DIST
    STATIC_URL_PATH = '/assets'

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    ALLOWED_UPLOAD_EXTENSIONS = {'png'}

    DUMMY_EMAIL_MODE = os.getenv("DUMMY_EMAIL_MODE").lower() in ('true', '1', 't')

    if not DUMMY_EMAIL_MODE:
        MAIL_SMTP_HOST = os.getenv("MAIL_SMTP_HOST")
        MAIL_SMTP_PORT = int(os.getenv("MAIL_SMTP_PORT", 587))
        MAIL_SMTP_USERNAME = os.getenv("MAIL_SMTP_USERNAME")
        MAIL_SMTP_PASSWORD = os.getenv("MAIL_SMTP_PASSWORD")
        MAIL_SMTP_TIMEOUT = int(os.getenv("MAIL_SMTP_TIMEOUT", 30))
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_BATCH_SIZE = int(os.getenv("MAIL_BATCH_SIZE", 100))
    MAIL_MAX_ATTEMPTS = int(os.getenv("MAIL_MAX_ATTEMPTS", 3))
    MAIL_BATCH_PAUSE_SEC = int(os.getenv("MAIL_BATCH_PAUSE_SEC", 5))

    DIFFICULTY_INDEX = {
        0: "Easy",
        1: "Moderate",
        2: "Difficult",
        3: "Very Difficult"
    }