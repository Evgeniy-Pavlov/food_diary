from django.contrib import admin
from .models import UserBase, UserStat, DirectoryFood

# Register your models here.
@admin.register(UserBase)
class AdminUser(admin.ModelAdmin):
    list_display = ('id', 'username', 'date_create', 'email', 'password')

@admin.register(UserStat)
class AdminUser(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'calories_burned')

@admin.register(DirectoryFood)
class AdminUser(admin.ModelAdmin):
    list_display = ('id', 'name', 'caloric', 'fat', 'carboon', 'protein')