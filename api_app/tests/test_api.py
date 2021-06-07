import json
import os
import sys
from collections import OrderedDict
from io import BytesIO


from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from django.core.files.uploadedfile import SimpleUploadedFile

import shutil

from api_app.permissions import CreateExpiredLinkPermission
from api_app.serializers import ImageListSerializer, ExpiredLinkCreateSerializer

from app_with_ui.models import User, AccountTier, Image, ThumbnailType, ExpiredLink
from PIL import Image as Img


class ImageApiTestCase(APITestCase):

    def setUp(self):
        self.thumbnail_type_original = ThumbnailType.objects.create(
            title='Original image',
            is_original=True
        )
        self.thumbnail_type_200px = ThumbnailType.objects.create(
            title='200px',
            heigth_size_in_pixels=200,
            is_original=False
        )

        self.account_tier_basic = AccountTier.objects.create(title='Basic')
        self.account_tier_enterprise = AccountTier.objects.create(
            title='Enterprise',
            has_ability_create_expiry_link=True
        )

        self.user_basic = User.objects.create(
            username='user_basic',
            password='test',
            account_tier=self.account_tier_basic
        )
        self.user_enterprise = User.objects.create(
            username='user_enterprise',
            password='test',
            account_tier=self.account_tier_enterprise
        )

        self.new_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=open('api_app/tests/book.jpeg', 'rb').read(),
            content_type='image/jpeg'
        )

    def generate_image_file(self):
        file = BytesIO()
        image = Img.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_all_images(self):
        self.original_image = Image.objects.create(
                user=self.user_basic,
                title='Test_original_image',
                type=self.thumbnail_type_original,
                image=self.new_file
            )
        self.original_image = Image.objects.create(
                user=self.user_basic,
                title='Test_200px_image',
                type=self.thumbnail_type_200px,
                image=self.new_file
            )

        url = reverse('image_list')

        response = self.client.get(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        self.client.force_authenticate(user=self.user_basic)
        image_type_200 = ThumbnailType.objects.filter(title='200px').first()
        image_type_original = ThumbnailType.objects.filter(is_original=True).first()

        basic_tier = AccountTier.objects.filter(title='Basic').first()

        basic_tier.allowed_image_types.add(image_type_200)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(200, response.data['results'][0]['type']['heigth_size_in_pixels'])

        basic_tier.allowed_image_types.add(image_type_original)
        response = self.client.get(url)
        self.assertEqual(2, response.data['count'])
        self.assertEqual(None, response.data['results'][0]['type']['heigth_size_in_pixels'])
        self.assertEqual(200, response.data['results'][1]['type']['heigth_size_in_pixels'])

        shutil.rmtree('media/user_basic', ignore_errors=True)

    def test_upload_image(self):
        url = reverse('upload')
        self.client.force_authenticate(user=self.user_enterprise)

        work_image = Img.open(self.generate_image_file())
        filestream = BytesIO()
        work_image.save(filestream, 'png', quality=90)
        filestream.seek(0)
        test_image = InMemoryUploadedFile(
                filestream, 'ImageField', 'file_name.png', 'jpeg/image', sys.getsizeof(filestream), None
            )

        data = {"id": 2, "title": "Test_upload_image", "image": test_image}
        self.assertEqual(0, Image.objects.filter(user=self.user_enterprise).count())
        self.assertEqual(0, Image.objects.filter(type__is_original=False, user=self.user_enterprise).count())
        response = self.client.post(url, data=data)
        self.assertEqual(1, Image.objects.filter(type__is_original=False, user=self.user_enterprise).count())
        self.assertEqual(2, Image.objects.filter(user=self.user_enterprise).count())
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        shutil.rmtree('media/user_enterprise', ignore_errors=True)

    def test_create_exp_link_get(self):

        url = 'http://127.0.0.1:8000/api/v1/exp_link_create/1/'
        self.client.force_authenticate(user=self.user_basic)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(CreateExpiredLinkPermission.message, response.data['detail'])

        self.account_tier_basic.has_ability_create_expiry_link = True
        response = self.client.get(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)





