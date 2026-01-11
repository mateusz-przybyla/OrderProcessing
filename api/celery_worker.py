from api import create_app
from api.celery_app import celery

app = create_app()