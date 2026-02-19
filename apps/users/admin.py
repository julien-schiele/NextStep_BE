from django.contrib import admin

from apps.users.models import User, UserActionToken

admin.site.register(User)
admin.site.register(UserActionToken)