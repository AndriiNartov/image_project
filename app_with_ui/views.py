import clipboard
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView

from app_with_ui.forms import UploadImageForm, ExpiryLinkCreateForm, LoginUserForm, \
    RegisterUserForm, ProfileForm
from app_with_ui.models import ThumbnailType, Image, ExpiredLink
from app_with_ui.services import get_original_image_size, resize_image, get_base64_encode_image, \
    set_link_expiring_datetime, is_link_expired, show_image_by_exp_link
from api_app.exceptions import OriginalImageTypeDoesNotExist


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'app_with_ui/index.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images_count'] = Image.objects.filter(
            user=self.request.user,
            type__in=self.request.user.account_tier.allowed_image_types.all()
        ).count()
        context['expiry_links_count'] = ExpiredLink.objects.filter(
            user=self.request.user,
            expiry_date_time__gt=timezone.now()
        ).count()
        return context


class ProfileView(LoginRequiredMixin, View):

    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        form = ProfileForm(
            initial={
                'account_tier': request.user.account_tier,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name
            }
        )
        return render(request, 'app_with_ui/profile.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST or None)
        if form.is_valid():
            user = request.user
            account_tier = form.cleaned_data['account_tier']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user.account_tier = account_tier
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return HttpResponseRedirect('/')
        return render(request, 'app_with_ui/profile.html', {'form': form})


class UploadImageView(LoginRequiredMixin, CreateView):

    login_url = '/login/'
    form_class = UploadImageForm
    model = Image
    template_name = 'app_with_ui/upload_image.html'

    def post(self, request, *args, **kwargs):
        form = UploadImageForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            try:
                image_type = ThumbnailType.objects.get(is_original=True)
            except ObjectDoesNotExist:
                raise OriginalImageTypeDoesNotExist
            original_image = form.save(commit=False)
            original_image.user = request.user
            original_image.type = image_type
            original_image.title = f'{original_image.title}(original image)'
            original_image.width, original_image.height = get_original_image_size(original_image.image)
            original_image.save()
            thumbnails_height_sizes_and_types = resize_image(original_image.image)
            for size_and_type in thumbnails_height_sizes_and_types:
                new_thumbnail_image, new_thumbnail_type, width, height = size_and_type
                Image.objects.create(
                    image=new_thumbnail_image,
                    type=new_thumbnail_type,
                    user=self.request.user,
                    title=f'{form.cleaned_data["title"]}({height}px thumbnail)',
                    width=width,
                    height=height)
            return HttpResponseRedirect('/')
        return render(request, 'app_with_ui/upload_image.html', {'form': form})


class ImageListView(LoginRequiredMixin, ListView):

    login_url = '/login/'
    model = Image
    template_name = 'app_with_ui/image_list.html'
    context_object_name = 'images'
    paginate_by = 6

    def get_queryset(self):
        images = Image.objects.filter(
            user=self.request.user,
            type__in=self.request.user.account_tier.allowed_image_types.all()
        ).order_by('-upload_date')
        return images


class CreateExpiryLinkView(LoginRequiredMixin, CreateView):

    login_url = '/login/'
    form_class = ExpiryLinkCreateForm
    template_name = 'app_with_ui/create_expiry_link.html'

    def get(self, request, *args, **kwargs):
        image = Image.objects.get(user=request.user, id=self.kwargs['pk'])
        if ExpiredLink.objects.filter(image=image).exists():
            expiring_link_obj = ExpiredLink.objects.filter(image=image).first()
            if is_link_expired(expiring_link_obj.expiry_date_time):
                expiring_link_obj.delete()
                return redirect('create_expiry_link', self.kwargs['pk'])
            return render(
                request,
                'app_with_ui/create_expiry_link.html',
                {'expiring_link_obj': expiring_link_obj}
            )
        form = ExpiryLinkCreateForm
        return render(request, 'app_with_ui/create_expiry_link.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = ExpiryLinkCreateForm(request.POST or None)
        if form.is_valid():
            image = Image.objects.get(user=request.user, id=self.kwargs['pk'])
            base64_encode_image = get_base64_encode_image(image.image.url)
            user_exp_time_seconds = form.cleaned_data['user_exp_time_seconds']
            expiry_date_time = set_link_expiring_datetime(user_exp_time_seconds)
            new_exp_link = ExpiredLink.objects.create(
                user=request.user,
                image=image,
                width=image.width,
                height=image.height,
                image_base_64=base64_encode_image,
                user_exp_time_seconds=user_exp_time_seconds,
                expiry_date_time=expiry_date_time,
                title=image.title
            )
            new_exp_link.expiry_link = f'http://127.0.0.1:8000/temp/{new_exp_link.uuid_link}/'
            new_exp_link.save()
            return redirect('create_expiry_link', self.kwargs['pk'])
        return render(request, 'app_with_ui/create_expiry_link.html', {'form': form})


class ExpiryLinksList(LoginRequiredMixin, ListView):

    login_url = '/login/'
    paginate_by = 6
    model = ExpiredLink
    template_name = 'app_with_ui/expiry_links_list.html'
    context_object_name = 'links'

    def get_queryset(self):
        links = ExpiredLink.objects.filter(expiry_date_time__gt=timezone.now())
        return links


class ShowImageByExpiryLink(View):

    def get(self, request, *args, **kwargs):
        return show_image_by_exp_link(self.kwargs['link'])


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'app_with_ui/registration.html'
    success_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.first_name = form.cleaned_data['name']
            new_user.last_name = form.cleaned_data['surname']
            new_user.account_tier = form.cleaned_data['account_tier']
            new_user.save()
            return redirect('login')
        return render(request, 'app_with_ui/registration.html', {'form': form})


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'app_with_ui/login.html'

    def get_success_url(self):
        return reverse_lazy('index')


def logout_user(request):
    logout(request)
    print('logout')
    return redirect('index')
