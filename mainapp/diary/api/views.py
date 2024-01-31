from http import HTTPStatus
from django.contrib.auth.views import LoginView, LogoutView
from diary.models import UserBase

class UserLoginView(LoginView):
    """Представление страницы авторизации"""
    model = UserBase
    success_url = '/'

class UserLogoutView(LogoutView):
    """Представление выхода авторизованного пользователя"""
    model = UserBase

