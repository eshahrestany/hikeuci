import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
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

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    FRONTEND_DIST = os.path.join(BASE_DIR, '..', 'frontend', 'dist')
    STATIC_FOLDER = os.path.join(FRONTEND_DIST, 'assets')
    TEMPLATE_FOLDER = FRONTEND_DIST
    STATIC_URL_PATH = '/assets'

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    ALLOWED_UPLOAD_EXTENSIONS = {'png'}
