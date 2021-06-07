from celery import shared_task
from django.utils import timezone

from .models import ExpiredLink

@shared_task
def delete_expired_links_from_db():
    print('HELLO THERE!')
    if ExpiredLink.objects.filter(expiry_date_time__lt=timezone.now()):
        ExpiredLink.objects.filter(expiry_date_time__lt=timezone.now()).delete()
        return ('Deleted')
    return ('No expired links to delete')
