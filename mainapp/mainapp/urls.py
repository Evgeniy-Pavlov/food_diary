"""
URL configuration for mainapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from diary.api.views import UserLoginView, UserLogoutView, UserRegisterView, FoodSearchView, UserFoodAddView, UserStatAddView,\
    DirectoryFoodUserCreateView, DirectoryIngredientsCreateView, RecipeCreateView, UserFoodDeleteView, DirectoryFoodUserDeleteView, \
    DirectoryIngredientsDeleteView, UserGetStatForDayView, RecipeDeleteView, UserGetStatForPeriodView, UserFoodDayStatView, UserFoodDayStatPeriodView, \
    UserChangePasswordView, UserGetInfoView \

schema_view = get_schema_view(
   openapi.Info(
      title="Diary API",
      default_version='v1',
      description="Diary description",
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('login/', UserLoginView.as_view()),
    path('logout/', UserLogoutView.as_view()),
    path('api/auth', TokenObtainPairView.as_view(), name='auth'),
    path('api/logout', TokenBlacklistView.as_view(), name= 'token_blacklist'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register', UserRegisterView.as_view(), name='user-create'),
    path('api/change-pwd/<int:pk>', UserChangePasswordView.as_view(), name='user change password'),
    path('api/food/search', FoodSearchView.as_view(), name='search_food'),
    path('api/user/foodstat/add', UserFoodAddView.as_view(), name='food_add_in_stat'),
    path('api/user/foodstat/day', UserFoodDayStatView.as_view(), name='food_stat_for_day'),
    path('api/user/foodstat/period', UserFoodDayStatPeriodView.as_view(), name='food_stat_for_period'),
    path('api/user/foodstat/delete/<int:pk>', UserFoodDeleteView.as_view(), name='food_delete_in_stat'),
    path('api/user/userstat/add', UserStatAddView.as_view(), name='user_calories_food_add'),
    path('api/food/add', DirectoryFoodUserCreateView.as_view(), name='create_food_user'),
    path('api/food/delete/<int:pk>', DirectoryFoodUserDeleteView.as_view(), name='delete_food_user'),
    path('api/food/ingredients/add', DirectoryIngredientsCreateView.as_view(), name = 'create_ingredients_in_the_directory'),
    path('api/food/ingredients/delete/<int:pk>', DirectoryIngredientsDeleteView.as_view(), name = 'delete_ingredients_in_the_directory'),
    path('api/food/recipe/create', RecipeCreateView.as_view(), name = 'create_recipe'),
    path('api/food/recipe/delete/<int:pk>', RecipeDeleteView.as_view(), name = 'delete_recipe'),
    path('api/user/stat-for-day', UserGetStatForDayView.as_view(), name = 'stat_for_day_user'),
    path('api/user/stat-for-period', UserGetStatForPeriodView.as_view(), name = 'stat_for_period_user'),
    path('api/user/userinfo', UserGetInfoView.as_view(), name= 'get_info_for_user')
]
