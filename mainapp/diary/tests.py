"""Модуль тестов API django приложения."""
import json
import datetime
from http import HTTPStatus
from django.test import TestCase
from .models import UserBase, DirectoryFood


# Create your tests here.
class TestUserRegister(TestCase):
    """Класс тестов таблицы UserBase и метода регистрации."""
    def test_register_valid(self):
        """Позитивный сценарий регистрации пользователя."""
        data = {'username': 'test_user', 'email': 'test_user@mail.com', 'password': 'Qwerty777!!'}
        response = self.client.post('/api/register', json.dumps(data),\
            content_type='application/json')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        result = response.json()
        self.assertEqual(result['username'], data['username'])
        self.assertEqual(result['email'], data['email'])

    def test_register_invalid(self):
        """Негативный сценарий регистрации пользователя и проверка обязательности
        заполнения полей."""
        data_1 = {'username': 'test_user_1', 'email': 'test_user@mail.com'}
        data_2 = {'username': 'test_user_2', 'password': 'Qwerty777!!'}
        data_3 = {'email': 'test_user_2@mail.com', 'password': 'Qwerty777!!'}
        response_1 = self.client.post('/api/register', json.dumps(data_1),\
            content_type='application/json')
        self.assertEqual(response_1.status_code, HTTPStatus.BAD_REQUEST)
        result = response_1.json()
        self.assertEqual(result['password'][0], 'This field is required.')
        response_2 = self.client.post('/api/register', json.dumps(data_2),\
            content_type='application/json')
        self.assertEqual(response_2.status_code, HTTPStatus.BAD_REQUEST)
        result = response_2.json()
        self.assertEqual(result['email'][0], 'This field is required.')
        response_3 = self.client.post('/api/register', json.dumps(data_3),\
            content_type='application/json')
        self.assertEqual(response_3.status_code, HTTPStatus.BAD_REQUEST)
        result = response_3.json()
        self.assertEqual(result['username'][0], 'This field is required.')


class TestSearchFood(TestCase):
    """Класс тестов поиска еды."""

    def test_search_food_from_database(self):
        """Позитивный сценарий поиска еды и проверки получения результата."""
        food = DirectoryFood.objects.create(name = 'Test_food',\
            caloric= 100, fat = 200, protein = 300, carbon = 400)
        response = self.client.get('/api/food/search?name=Test_food&lang=en')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        result = response.json()[0]
        self.assertEqual(result['name'], food.name)
        self.assertEqual(result['caloric'], food.caloric)
        self.assertEqual(result['fat'], food.fat)
        self.assertEqual(result['protein'], food.protein)
        self.assertEqual(result['carbon'], food.carbon)

class TestUserStatFodDay(TestCase):
    """Класс тестов получения и добавления статистики
    пользователя за день."""

    def test_stat_from_day_without_stat(self):
        """Позитивный сценарий получения статистики пользователя,
        для которого нет записи."""
        data = {'username': 'test_user', 'email': 'test_user@mail.com', 'password': 'Qwerty777!!'}
        response_reg = self.client.post('/api/register', json.dumps(data),\
            content_type='application/json')
        username = response_reg.json()['username']
        user = UserBase.objects.get(username=username)
        response = self.client.get(f'/api/user/stat-for-day?date=2020-01-01&user={user.id}')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        result = response.json()
        self.assertEqual(user.id, int(result['user']))
        self.assertEqual('2020-01-01', result['date'])
        self.assertEqual(0, result['calories_burned'])

    def test_user_foodstat_add(self):
        """Позитивный сценарий добавления статистики пользователя."""
        data = {'username': 'test_user_food', 'email': 'test_user_food@mail.com',\
            'password': 'Qwerty777!!'}
        response_reg = self.client.post('/api/register', json.dumps(data),\
            content_type='application/json')
        username = response_reg.json()['username']
        user = UserBase.objects.get(username=username)
        food = DirectoryFood.objects.create(name = 'Test_food', caloric= 100,\
            fat = 200, protein = 300, carbon = 400)
        user_auth = self.client.post('/api/auth', json.dumps({'username': user.username,\
            'password': data['password']}), content_type='application/json')
        token = user_auth.json()['access']
        today = datetime.datetime.today()
        time = today.strftime('%Y-%m-%d')
        data = {'food': food.id, 'user': user.id, 'date': time}
        response = self.client.post('/api/user/foodstat/add', json.dumps(data),\
            content_type='application/json', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        result = response.json()
        self.assertEqual(result['user'], user.id)
        self.assertEqual(result['calories_burned'], food.caloric)
        self.assertEqual(result['date'], time)


class TestFoodStatAdd(TestCase):
    """Класс тестов получения статистики и добавления блюд пользователя за день."""

    def setUp(self):
        data = {'username': 'test_user_food', 'email': 'test_user_food@mail.com',\
            'password': 'Qwerty777!!'}
        response_reg = self.client.post('/api/register', json.dumps(data),\
            content_type='application/json')
        username = response_reg.json()['username']
        self.user = UserBase.objects.get(username=username)
        self.food_1 = DirectoryFood.objects.create(name = 'Test_food',\
            caloric= 100, fat = 200, protein = 300, carbon = 400)
        self.food_2 = DirectoryFood.objects.create(name = 'Test_food_2',\
            caloric= 200, fat = 400, protein = 600, carbon = 800)
        user_auth = self.client.post('/api/auth', json.dumps({\
            'username': self.user.username, 'password': data['password']}),\
            content_type='application/json')
        self.token = user_auth.json()['access']
        today = datetime.datetime.today()
        self.time = today.strftime('%Y-%m-%d')

    def test_userstat_add(self):
        """Позитивный сценарий добавления статистики по блюдам пользователя."""
        response = self.client.post('/api/user/userstat/add',\
            json.dumps({'user': self.user.id, 'calories_burned': self.food_1.caloric,\
            'date': self.time}), content_type='application/json',\
            headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        result = response.json()
        self.assertEqual(result['user'], self.user.id)
        self.assertEqual(result['date'], self.time)
        self.assertEqual(result['calories_burned'], self.food_1.caloric)
        response = self.client.post('/api/user/userstat/add',\
            json.dumps({'user': self.user.id, 'calories_burned': self.food_2.caloric,\
            'date': self.time}), content_type='application/json',\
            headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        result = response.json()
        self.assertEqual(result['user'], self.user.id)
        self.assertEqual(result['date'], self.time)
        self.assertEqual(result['calories_burned'], self.food_1.caloric + self.food_2.caloric)
