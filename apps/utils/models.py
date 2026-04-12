from django.db import models
import uuid
from parler.models import TranslatableModel, TranslatedFields


class AbstractTimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AbstractBaseUUID(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class PrivacyPolicy(AbstractBaseUUID, AbstractTimeStamped, TranslatableModel):
    translations = TranslatedFields(
        short_text=models.TextField(help_text="Short version of privacy policy"),
        long_text=models.TextField(help_text="Long version of privacy policy"),
    )

    def __str__(self):
        return f"PrivacyPolicy (updated {self.updated_at})"
