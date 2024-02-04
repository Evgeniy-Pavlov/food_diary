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
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from diary.api.views import UserLoginView, UserLogoutView, UserRegisterView, FoodSearchView, UserFoodAddView, UserStatAddView, DirectoryFoodUserCreateView


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
    path('api/auth/', TokenObtainPairView.as_view(), name='auth'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', UserRegisterView.as_view(), name='user-create'),
    path('api/food/search/', FoodSearchView.as_view(), name='search_food'),
    path('api/user/foodstat/add/', UserFoodAddView.as_view(), name='food_add_in_stat'),
    path('api/user/userstat/add/', UserStatAddView.as_view(), name='user_calories_food_add'),
    path('api/food/add/', DirectoryFoodUserCreateView.as_view(), name='create_food_user')
]
