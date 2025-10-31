from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from dirtyfields import DirtyFieldsMixin
from rest_framework.exceptions import ValidationError
from core.models import TimeStampedModel
from django.contrib.auth.models import BaseUserManager
from management_api.models import PlattformSettings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, DirtyFieldsMixin, TimeStampedModel):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    coins = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    password = models.CharField(max_length=128, blank=True, null=True)
    keycloak_id = models.UUIDField(null=True, unique=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def clean(self):
        super().clean()
        try:
            coin_limit = PlattformSettings.objects.get(id=1).coin_limit
        except PlattformSettings.DoesNotExist:
            coin_limit = 10000.00

        if self.coins > coin_limit:
            raise ValidationError(f"Coins cannot exceed the limit of {coin_limit}")

    def save(self, *args, **kwargs):
        if not self.email:
            self.email = f"{self.username}@fallback.com"

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
