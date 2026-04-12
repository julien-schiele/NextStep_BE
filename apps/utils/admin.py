from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import PrivacyPolicy


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(TranslatableAdmin):
    list_display = ("updated_at",)
