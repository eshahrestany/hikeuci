import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    FRONTEND_DIST = os.path.join(BASE_DIR, '..', 'frontend', 'dist')
    STATIC_FOLDER = os.path.join(FRONTEND_DIST, 'assets')
    TEMPLATE_FOLDER = FRONTEND_DIST
    STATIC_URL_PATH = '/assets'
