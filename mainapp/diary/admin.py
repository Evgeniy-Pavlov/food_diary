from django.contrib import admin
from .models import UserBase

# Register your models here.
@admin.register(UserBase)
class AdminUser(admin.ModelAdmin):
    list_display = ('id', 'username', 'date_create', 'email', 'password')
