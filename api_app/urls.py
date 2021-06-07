from django.urls import path

from api_app.views import CreateImage, ImageListView, ExpiredLinkCreateView

urlpatterns = [
    path('upload/', CreateImage.as_view(), name='upload'),
    path('images/', ImageListView.as_view(), name='image_list'),
    path('exp_link_create/<int:pk>/', ExpiredLinkCreateView.as_view(), name='exp_link_create'),

]