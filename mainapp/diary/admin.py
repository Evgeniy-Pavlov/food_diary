from django.contrib import admin
from .models import UserBase, UserStat, DirectoryFood, UserFoodDay

# Register your models here.
@admin.register(UserBase)
class AdminUser(admin.ModelAdmin):
    list_display = ('id', 'username', 'date_create', 'email', 'password')

@admin.register(UserStat)
class AdminUserStat(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'calories_burned')

@admin.register(DirectoryFood)
class AdminDirectoryFood(admin.ModelAdmin):
    list_display = ('id', 'name', 'caloric', 'fat', 'carbon', 'protein', 'user_create')

@admin.register(UserFoodDay)
class AdminUserFoodDay(admin.ModelAdmin):
    list_display = ('id', 'food', 'user', 'date')
