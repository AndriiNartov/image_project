from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import *


class UploadImageForm(forms.ModelForm):

    title = forms.CharField(
        required=True,
        label='Title',
        widget=forms.TextInput(
            attrs={'class': "form-control", 'type': "text"}
        )
    )

    image = forms.ImageField(
        widget=forms.FileInput(
            attrs={'type': 'file', 'id': 'inputGroupFile01', 'class': 'custom-file-input'}
        )
    )

    class Meta:
        model = Image
        fields = ['title', 'image']


class ExpiryLinkCreateForm(forms.ModelForm):

    class Meta:
        model = ExpiredLink
        fields = ['user_exp_time_seconds']


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'type': "text",
                   'id': "inputLogin",
                   'class': 'form-control',
                   'required': 'required',
                   'autofocus': 'autofocus'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'type': "password", 'id': "inputPassword", 'class': 'form-control', 'autofocus': 'autofocus'}
        )
    )


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'type': "text", 'id': "inputLogin", 'class': 'form-control', 'autofocus': 'autofocus'}
        )
    )
    password1 = forms.CharField(
        label='Password',
        required=True,
        widget=forms.PasswordInput(
            attrs={'type': "password", 'id': "inputPassword", 'class': 'form-control', 'required': 'required'}
        )
    )
    password2 = forms.CharField(required=False)
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'type': "text", 'id': "inputLogin", 'class': 'form-control'}
        )
    )
    surname = forms.CharField(
        widget=forms.TextInput(
            attrs={'type': "text", 'id': "inputLogin", 'class': 'form-control'}
        )
    )
    account_tier = forms.ModelChoiceField(
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control'}),
        queryset=AccountTier.objects.all(),
        empty_label='Choose account tier'
    )

    class Meta:
        model = User
        fields = ('username', 'name', 'surname', 'password1', 'account_tier')


class ProfileForm(forms.ModelForm):

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'type': "text", 'id': "inputLogin", 'class': 'form-control'}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'type': "text", 'id': "inputLogin", 'class': 'form-control'}
        )
    )

    account_tier = forms.ModelChoiceField(
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control'}),
        queryset=AccountTier.objects.all(),
        empty_label='Choose account tier'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'account_tier']
