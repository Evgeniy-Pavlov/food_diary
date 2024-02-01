from http import HTTPStatus
from django.contrib.auth.views import LoginView, LogoutView
from diary.models import UserBase
from rest_framework.views import APIView

class UserLoginView(LoginView):
    """Представление страницы авторизации"""
    model = UserBase
    success_url = '/'

class UserLogoutView(LogoutView):
    """Представление выхода авторизованного пользователя"""
    model = UserBase

