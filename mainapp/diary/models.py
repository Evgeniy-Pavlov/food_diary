from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.
class UserBase(AbstractUser):
    """Базовая таблица пользователей."""
    username = models.CharField(unique=True, max_length=40)
    date_create = models.DateField(default=datetime.now)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name_plural = 'UserBase'