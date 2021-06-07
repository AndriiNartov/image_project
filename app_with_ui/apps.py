from django.apps import AppConfig


class AppWithUiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_with_ui'
