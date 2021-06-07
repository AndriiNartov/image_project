from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
import uuid


class User(AbstractUser):
    account_tier = models.ForeignKey(
        'AccountTier',
        on_delete=models.CASCADE,
        verbose_name='Account tier',
        blank=True, null=True
    )


class AccountTier(models.Model):
    title = models.CharField(max_length=30, verbose_name='Name of account tier')
    allowed_image_types = models.ManyToManyField('ThumbnailType', verbose_name='Allowed types of images')
    has_ability_create_expiry_link = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ThumbnailType(models.Model):
    title = models.CharField(max_length=50, verbose_name='Name of thumbnail')
    heigth_size_in_pixels = models.PositiveSmallIntegerField(blank=True, null=True)
    is_original = models.BooleanField(default=True, verbose_name='Image has original size')

    def __str__(self):
        return self.title


def upload_image(instance, filename):
    return '/'.join([instance.user.username, instance.type.title, filename])


class Image(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='images',
        blank=True,
        null=True
    )
    type = models.ForeignKey(
        ThumbnailType,
        on_delete=models.CASCADE,
        related_name='thumbnail_links',
        verbose_name='Type of thumbnail',
        blank=True,
        null=True
    )
    title = models.CharField(max_length=50, verbose_name='Image title')
    image = models.ImageField(upload_to=upload_image, validators=[FileExtensionValidator(['png', 'jpeg', 'jpg'])])
    width = models.PositiveIntegerField(blank=True, null=True, verbose_name='Width')
    height = models.PositiveIntegerField(blank=True, null=True, verbose_name='Height')
    upload_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f'{self.title}'


class ExpiredLink(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='expired_links',
        blank=True,
        null=True
    )
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='expired_links', verbose_name='Image')
    title = models.CharField(max_length=100, verbose_name='Name of link')
    width = models.PositiveIntegerField(blank=True, null=True, verbose_name='Width')
    height = models.PositiveIntegerField(blank=True, null=True, verbose_name='Height')
    uuid_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    expiry_link = models.URLField(verbose_name='Expiry link for user', null=True)
    user_exp_time_seconds = models.PositiveSmallIntegerField(
        verbose_name='Expiry time in seconds',
        validators=[
            MinValueValidator(300, message='Value must be between 300 and 30000 seconds'),
            MaxValueValidator(30000, message='Value must be between 300 and 30000 seconds'),
        ]
    )
    expiry_date_time = models.DateTimeField(blank=True, null=True, verbose_name='Expiry date and time')
    image_base_64 = models.BinaryField(verbose_name='Image in base64 format')

    def __str__(self):
        return self.title
