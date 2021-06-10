from celery import shared_task
import os

from .models import ExpiredLink
from .services import is_link_expired, delete_expired_link_image


@shared_task
def delete_expired_images():
    print('I am here to destroy!')
    for username in os.listdir('media/temp'):
        for dir in os.listdir(f'media/temp/{username}'):
            if ExpiredLink.objects.filter(uuid_link=dir).exists():
                expiring_link_obj = ExpiredLink.objects.filter(uuid_link=dir).first()
                if is_link_expired(expiring_link_obj.expiry_date_time):
                    delete_expired_link_image(dir, username)
                    expiring_link_obj.delete()
            else:
                delete_expired_link_image(dir, username)

