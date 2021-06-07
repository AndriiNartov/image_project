import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_project.settings')

app = Celery('image_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'deleting_expired_links': {
        'task': 'app_with_ui.tasks.delete_expired_links_from_db',
        'schedule': 1.0
    }
}

#  celery -A image_project beat
# celery -A image_project worker -l INFO