import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from common.utils import dynamic_upload_path

from common.models import NormalizedEmailField


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, is_superuser=False, **extra_fields):
        if not email:
            raise ValueError("Please enter email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        user.is_staff = is_superuser
        user.is_superuser = is_superuser

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(
            email, password=password, is_superuser=True, is_staff=True, **extra_fields
        )

        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, null=True, blank=True)
    email = NormalizedEmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Email verified
    is_email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    # Email verification token
    email_verification_token = models.CharField(max_length=255, null=True, blank=True)

    profile_picture = models.ImageField(
        upload_to=dynamic_upload_path, null=True, blank=True, max_length=500
    )

    objects = UserAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    otp = models.CharField(max_length=8, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    otp_sent_at = models.DateTimeField(null=True, blank=True)

    # Auto generated Username
    def save(self, *args, **kwargs):
        if not self.username:
            # Add random UUID to the end of the username
            self.username = (
                self.first_name.lower() + self.last_name.lower() + str(uuid.uuid4())[:8]
            )
        super().save(*args, **kwargs)

    @property
    def name(self):
        first_name = self.first_name
        last_name = f"{self.last_name[0]}." if self.last_name else ""
        return f"{first_name} {last_name}".strip()

    def __str__(self):
        last_name = f"{self.last_name[0]}." if self.last_name else ""
        name = self.name or self.first_name + " " + last_name
        formatted_name = name[:50] + "..." if len(name) > 50 else name
        return formatted_name + " - " + self.email

    class Meta:
        indexes = [
            # Single column indexes for commonly queried fields
            models.Index(fields=["username"], name="user_username_idx"),
            models.Index(fields=["is_active"], name="user_is_active_idx"),
            models.Index(
                fields=["is_email_verified"], name="user_is_email_verified_idx"
            ),
            models.Index(
                fields=["email_verification_token"],
                name="email_verification_token_idx",
            ),
            models.Index(fields=["created_at"], name="user_created_at_idx"),
            models.Index(fields=["otp_expiry"], name="user_otp_expiry_idx"),
            models.Index(fields=["is_staff"], name="user_is_staff_idx"),
            models.Index(fields=["is_superuser"], name="user_is_superuser_idx"),
            # Composite indexes for common query patterns
            models.Index(
                fields=["is_active", "is_email_verified"],
                name="user_active_verified_idx",
            ),
            models.Index(
                fields=["is_active", "created_at"], name="user_active_created_at_idx"
            ),
        ]
