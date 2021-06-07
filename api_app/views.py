from rest_framework import generics
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.pagination import PageNumberPagination

from api_app.exceptions import ImageDoesNotExist, OriginalImageTypeDoesNotExist
from app_with_ui.models import Image, ThumbnailType
from api_app.permissions import CreateExpiredLinkPermission, HasUserAccountTier
from api_app.serializers import ImageListSerializer, ExpiredLinkCreateSerializer, ImageSerializer
from app_with_ui.services import resize_image, set_link_expiring_datetime, get_base64_encode_image, \
    get_original_image_size
from image_project.settings import domain_and_port_for_link


class ImageListPagination(PageNumberPagination):

    page_size = 3
    page_query_param = 'page'
    max_page_size = 10


class CreateImage(CreateAPIView):
    """Allows to upload image by POST request to 'upload/' """

    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            image_type = ThumbnailType.objects.get(is_original=True)
        except ObjectDoesNotExist:
            raise OriginalImageTypeDoesNotExist
        _serializer = serializer.save(user=self.request.user, type=image_type)
        _serializer.width, _serializer.height = get_original_image_size(_serializer.image)
        _serializer.save()
        thumbnails_height_sizes_and_types = resize_image(_serializer.image)
        for size_and_type in thumbnails_height_sizes_and_types:
            new_thumbnail_image, new_thumbnail_type, width, height = size_and_type
            Image.objects.create(
                image=new_thumbnail_image,
                type=new_thumbnail_type,
                user=self.request.user,
                title=f'{_serializer.title}({height}px thumbnail)',
                width=width,
                height=height
            )


class ImageListView(generics.ListAPIView):
    """Allows to get list of all user's images according to account tier by GET request to 'images/' """

    permission_classes = [IsAuthenticated, HasUserAccountTier]
    pagination_class = ImageListPagination
    serializer_class = ImageListSerializer

    def get_queryset(self):

        return Image.objects.filter(
            user=self.request.user,
            type__in=self.request.user.account_tier.allowed_image_types.all()
        )


class ExpiredLinkCreateView(CreateAPIView):
    """Allows to generate expiry link by POST request to 'exp_link_create/<image_id>/' """

    serializer_class = ExpiredLinkCreateSerializer
    permission_classes = [IsAuthenticated, CreateExpiredLinkPermission]

    def perform_create(self, serializer):
        try:
            image = Image.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            raise ImageDoesNotExist

        user_exp_time_seconds = serializer.validated_data['user_exp_time_seconds']
        link_exp_datetime = set_link_expiring_datetime(user_exp_time_seconds)
        title = f'{image.title}_{image.type.title}_expiry'
        image_base_64 = get_base64_encode_image(image.image.url)
        _serializer = serializer.save(
            user=self.request.user,
            expiry_date_time=link_exp_datetime,
            image=image,
            user_exp_time_seconds=user_exp_time_seconds,
            title=title,
            image_base_64=image_base_64
        )
        _serializer.expiry_link = f'{domain_and_port_for_link}/temp/{_serializer.uuid_link}'
        _serializer.save()