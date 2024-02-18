from django.contrib import admin
from .models import UserBase, UserStat, DirectoryFood, UserFoodDay, DirectoryIngredients, RecipeFood

# Register your models here.
@admin.register(UserBase)
class AdminUser(admin.ModelAdmin):
    list_display = ('id', 'username', 'date_create', 'email', 'password')

@admin.register(UserStat)
class AdminUserStat(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'calories_burned', 'fat_burned', 'protein_burned', 'carbon_burned')

@admin.register(DirectoryFood)
class AdminDirectoryFood(admin.ModelAdmin):
    list_display = ('id', 'name', 'caloric', 'fat', 'carbon', 'protein', 'user_create')

@admin.register(UserFoodDay)
class AdminUserFoodDay(admin.ModelAdmin):
    list_display = ('id', 'food', 'user', 'date')

@admin.register(DirectoryIngredients)
class AdminDirectoryIngredients(admin.ModelAdmin):
    list_display = ('id', 'name', 'caloric', 'fat', 'carbon', 'protein', 'user_create')

@admin.register(RecipeFood)
class AdminRecipeFood(admin.ModelAdmin):
    list_display = ('id', 'food', 'ingredient', 'gram')
