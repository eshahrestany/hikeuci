from celery.schedules import crontab
from app import create_app

flask_app = create_app()
celery_app = flask_app.extensions["celery"]
celery_app.conf.imports = "app.tasks"
celery_app.conf.beat_schedule = {
    'update_phase_every_min': {
        'task': 'app.tasks.check_and_update_phase',
        'schedule': crontab()
    }
}