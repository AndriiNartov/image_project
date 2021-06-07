from app_with_ui.models import Image, ExpiredLink, ThumbnailType
from rest_framework import serializers


class ThumbnailTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ThumbnailType
        fields = ['title', 'heigth_size_in_pixels']


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['id', 'title', 'image']


class ImageListSerializer(serializers.ModelSerializer):
    type = ThumbnailTypeSerializer()

    class Meta:
        model = Image
        fields = ['title', 'id', 'image', 'type']


class ExpiredLinkCreateSerializer(serializers.ModelSerializer):
    user_exp_time_seconds = serializers.IntegerField(required=True, min_value=300, max_value=30000)
    expiry_link = serializers.CharField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    image = ImageSerializer(read_only=True)
    expiry_date_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ExpiredLink
        fields = ['user_exp_time_seconds', 'expiry_link', 'user', 'image', 'expiry_date_time']