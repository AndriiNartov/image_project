from django.urls import path

from app_with_ui.views import IndexView, UploadImageView, ImageListView, CreateExpiryLinkView, \
    ExpiryLinksList, ShowImageByExpiryLink, CopyExpiryLink, LoginUser, RegisterUser, ProfileView, logout_user

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('upload-image', UploadImageView.as_view(), name='upload_image'),
    path('all-images', ImageListView.as_view(), name='all_images'),
    path('create-expiry-link/<int:pk>/', CreateExpiryLinkView.as_view(), name='create_expiry_link'),
    path('all-expired-links/', ExpiryLinksList.as_view(), name='all_expired_links'),
    path('temp/<str:link>/', ShowImageByExpiryLink.as_view(), name='show_image_by_exp_link'),
    path('copy-expiry-link/<str:link>/', CopyExpiryLink.as_view(), name='copy_expiry_link'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', logout_user, name='logout'),
]