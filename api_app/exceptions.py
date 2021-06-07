from rest_framework.exceptions import APIException


class ImageDoesNotExist(APIException):
    """Message of exception if image object does not exist in database"""
    status_code = 500
    default_detail = 'Image does not exist'
    default_code = 'image_does_not_exist'


class OriginalImageTypeDoesNotExist(APIException):
    """Message of exception if type for original image was not created via admin panel and does not exist in database"""
    status_code = 500
    default_detail = 'There is no created type for original image  in DB.' \
                     'You should create this type via admin panel in Thumbnail types section'
    default_code = 'thumbnail_type_does_not_exist'