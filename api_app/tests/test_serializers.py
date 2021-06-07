import shutil
from collections import OrderedDict

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from api_app.serializers import ImageSerializer, ImageListSerializer
from app_with_ui.models import ThumbnailType, AccountTier, User, Image


class ImageSerializerTestCase(TestCase):

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

    def test_image_serializer(self):

        original_image = Image.objects.create(
            user=self.user_basic,
            title='Test_original_image',
            type=self.thumbnail_type_original,
            image=self.new_file
        )
        data = ImageSerializer(original_image).data

        expected_data = {
            'id': 1,
            'title': 'Test_original_image',
            'image': '/media/user_basic/Original%20image/test_image.jpg'
        }
        self.assertEqual(data, expected_data)

        shutil.rmtree('media/user_basic', ignore_errors=True)

    def test_image_list_serializer(self):

        original_image = Image.objects.create(
            user=self.user_enterprise,
            title='Test_original_image',
            type=self.thumbnail_type_original,
            image=self.new_file
        )

        data = ImageListSerializer(original_image).data

        expected_data = {
            'title': 'Test_original_image',
            'id': 1,
            'image': '/media/user_enterprise/Original%20image/test_image.jpg',
            'type': OrderedDict([('title', 'Original image'), ('heigth_size_in_pixels', None)])
        }
        self.assertEqual(data, expected_data)
        shutil.rmtree('media/user_enterprise', ignore_errors=True)
