import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

MAGIC_LINK_TTL = timedelta(minutes=15)


class Role(models.TextChoices):
    USER = "user", "User"
    MANAGER = "manager", "Room manager"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _normalise(self, email):
        if not email:
            raise ValueError("An email address is required.")
        return self.normalize_email(email.strip()).lower()

    def create_user(self, email, role=Role.USER, **extra_fields):
        user = self.model(email=self._normalise(email), role=role, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        user = self.model(email=self._normalise(email), role=Role.MANAGER, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Email-only account. There is no password; people sign in with a magic link."""

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def is_manager(self):
        return self.role == Role.MANAGER

    def toggle_role(self):
        self.role = Role.USER if self.is_manager else Role.MANAGER
        self.save(update_fields=["role"])

    def to_dict(self):
        return {"id": self.id, "email": self.email, "role": self.role, "is_manager": self.is_manager}


def generate_token():
    return secrets.token_urlsafe(32)


class MagicLink(models.Model):
    """A single-use, time-limited sign-in token."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="magic_links")
    token = models.CharField(max_length=64, unique=True, default=generate_token)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Magic link for {self.user.email}"

    @property
    def is_valid(self):
        return self.used_at is None and self.created_at >= timezone.now() - MAGIC_LINK_TTL

    def consume(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])
