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

class UserStat(models.Model):
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(default=datetime.now)
    calories_burned = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'UserStat'

class DirectoryFood(models.Model):
    name = models.CharField(unique=True, max_length=50)
    caloric = models.IntegerField(default=0)
    fat = models.IntegerField(default=0)
    carboon = models.IntegerField(default=0)
    protein = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'DirectoryFood'