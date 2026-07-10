import uuid
from pathlib import Path

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if email:
            email = self.normalize_email(email)

        directory = f"{uuid.uuid4().hex[:12]}"

        user = self.model(email=email, username=username, directory=directory, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    fullname = models.TextField(max_length=80, blank=True)
    directory = models.TextField(max_length=20, blank=True)

    objects = UserManager()

def user_upload_path(instance, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex[:8]}{ext}"
    return str(Path("uploads") / instance.owner.directory / unique_name)


class File(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="files")
    file = models.FileField(upload_to=user_upload_path)
    original_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    size_bytes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    downloaded_at = models.DateTimeField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.original_name)
