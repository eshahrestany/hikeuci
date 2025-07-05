import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = (
            os.getenv("DATABASE_URL") or f"sqlite:///{os.path.join(BASE_DIR, 'hike.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
