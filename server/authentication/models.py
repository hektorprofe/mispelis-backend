from django.contrib.auth.models import AbstractUser
from django.db import models


def path_to_avatar(instance, filename):
    return f'avatars/{instance.id}/{filename}'


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=150, unique=True)
    avatar = models.ImageField(
        upload_to=path_to_avatar, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']
