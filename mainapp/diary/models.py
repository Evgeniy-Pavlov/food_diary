"""Модуль с классами описывающими таблицы БД."""
from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserBase(AbstractUser):
    """Базовая таблица пользователей."""
    username = models.CharField(unique=True, max_length=40)
    date_create = models.DateField(default=datetime.now)
    email = models.EmailField(unique=True)

    class Meta:
        """Метакласс таблицы пользователей."""
        verbose_name_plural = 'UserBase'

class UserStat(models.Model):
    """Таблица статистики пользователя по калориям,
    жирам, белкам и углеводам за день."""
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE, null=False)
    date = models.DateField(auto_now_add=True)
    calories_burned = models.IntegerField(default=0)
    fat_burned = models.IntegerField(default=0)
    protein_burned = models.IntegerField(default=0)
    carbon_burned = models.IntegerField(default=0)

    class Meta:
        """Метакласс таблицы статистики пользователя."""
        verbose_name_plural = 'UserStat'

class DirectoryFood(models.Model):
    """Таблица справочник блюд."""
    name = models.CharField(unique=True, max_length=50)
    caloric = models.IntegerField(default=0)
    fat = models.IntegerField(default=0)
    carbon = models.IntegerField(default=0)
    protein = models.IntegerField(default=0)
    user_create = models.ForeignKey(UserBase, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=2000, null=True)

    class Meta:
        """Метакласс таблицы справочника блюд."""
        verbose_name_plural = 'DirectoryFood'

class UserFoodDay(models.Model):
    """Таблица блюд пользователя за день."""
    food = models.ForeignKey(DirectoryFood, on_delete=models.CASCADE)
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    class Meta:
        """Метакласс таблицы еды пользователя за день."""
        verbose_name_plural = 'UserFoodDay'

class DirectoryIngredients(models.Model):
    """Таблица справочник ингредиентов."""
    name = models.CharField(unique=True, max_length=50)
    caloric = models.IntegerField(default=0)
    fat = models.IntegerField(default=0)
    carbon = models.IntegerField(default=0)
    protein = models.IntegerField(default=0)
    user_create = models.ForeignKey(UserBase, on_delete=models.SET_NULL, null=True)

    class Meta:
        """Метакласс таблицы справочнике ингредиентов."""
        verbose_name_plural = 'DirectoryIngredients'

class RecipeFood(models.Model):
    """Таблица рецептов блюд."""
    food = models.ForeignKey(DirectoryFood, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(DirectoryIngredients, on_delete=models.CASCADE)
    gram = models.IntegerField(default=0)

    class Meta:
        """Метакласс таблицы рецептов."""
        verbose_name_plural = 'RecipeFood'
