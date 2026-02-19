from apps.users.choices import ActionChoices
from apps.utils.models import AbstractBaseUUID, AbstractTimeStamped
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
import uuid
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est requis")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser doit avoir is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser doit avoir is_superuser=True")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUUID, AbstractTimeStamped, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserActionToken(AbstractBaseUUID, AbstractTimeStamped, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="action_tokens",
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    expires_at = models.DateTimeField()
    action = models.CharField(
        max_length=32,
        choices=ActionChoices.choices,
        default=ActionChoices.RESET_PASSWORD,
    )

    class Meta:
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user", "action"]),
        ]

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.user} - {self.action}"
