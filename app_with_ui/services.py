from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse
from django.utils import timezone

import base64
import sys
from PIL import Image as img
from io import BytesIO
from datetime import timedelta

from app_with_ui.models import ThumbnailType, ExpiredLink


def get_original_image_size(image):
    original_image = img.open(image)
    width, height = original_image.size
    return width, height


def resize_image(image) -> list:
    """Resizing ogirinal image to thumbnails according thumbnail types defined via admin panel"""

    image_format = str(image).split('.')[-1]
    file_name = str(image).split('/')[-1]
    if image_format == 'jpg':
        image_format = 'jpeg'
    heigth_sizes = []
    heigth_sizes_and_types = []
    types = ThumbnailType.objects.all()

    for thumbnail_type in types:
        if thumbnail_type.heigth_size_in_pixels:
            heigth_sizes.append(thumbnail_type.heigth_size_in_pixels)

    for new_heigth in heigth_sizes:
        work_image = img.open(image)
        width, heigth = work_image.size
        new_width = int(new_heigth * (width / heigth))
        new_size = (new_width, new_heigth)
        work_image.thumbnail(new_size)
        filestream = BytesIO()
        work_image.save(filestream, f'{image_format.upper()}', quality=90)
        filestream.seek(0)
        thumbnail_type = ThumbnailType.objects.get(heigth_size_in_pixels=new_heigth)
        thumbnail_image = InMemoryUploadedFile(
                filestream, 'ImageField', file_name, 'jpeg/image', sys.getsizeof(filestream), None
            )
        image_and_type = (thumbnail_image, thumbnail_type, new_width, new_heigth)
        heigth_sizes_and_types.append(image_and_type)
    return heigth_sizes_and_types


def set_link_expiring_datetime(user_expiry_time_seconds):
    now = timezone.now()
    exp_datetime_seconds = timedelta(seconds=user_expiry_time_seconds)
    link_exp_datetime = now + exp_datetime_seconds
    return link_exp_datetime


def get_base64_encode_image(path):
    """Converting image into base64 format for storing in DB"""
    image = open(path[1:], 'rb')
    image_64_encode = base64.b64encode(image.read())
    image.close()
    return image_64_encode


def is_link_expired(link_expiring_date_time):
    """Checking if link is expired"""

    now = timezone.now()
    return now > link_expiring_date_time


def show_image_by_exp_link(link):
    """
    This function was created to make sure that expiry link works and
    user can get an image by this link.
    Also it demonstrate that link can be expired.
    If you will try go for it after the time is up you get error message instead of image
    """
    try:
        if ExpiredLink.objects.filter(uuid_link=link).exists():
            expiring_link_obj = ExpiredLink.objects.filter(uuid_link=link).first()
            if is_link_expired(expiring_link_obj.expiry_date_time):
                expiring_link_obj.delete()
                return HttpResponse('Your link is expired :(')
            else:
                img_base_64 = expiring_link_obj.image_base_64
                image_64_decode = base64.b64decode(img_base_64)
                img_file = BytesIO(image_64_decode)
                decoded_image = img.open(img_file)
                decoded_image.show()
                return HttpResponse('Image by your link was opened in separate window!')
        return HttpResponse('Your link is expired :(')
    except ExpiredLink.DoesNotExist:
        return HttpResponse('Your link is expired :(')
    except ValidationError:
        return HttpResponse('Your link is incorrect :(')





