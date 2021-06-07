from django.contrib import admin

from .models import *

admin.site.register(User)
admin.site.register(AccountTier)
admin.site.register(ThumbnailType)
admin.site.register(Image)
admin.site.register(ExpiredLink)

