import os
from http import HTTPStatus
import requests
from dotenv import dotenv_values
from drf_yasg import openapi
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from diary.models import UserBase, DirectoryFood, UserFoodDay, UserStat, DirectoryIngredients, RecipeFood
from django.db.utils import IntegrityError
from .serializers import UserRegisterSerializer, SearchFoodSerializer, SearchQueryParamSerializer, UserFoodDaySerializer, \
     UserStatAddSerializer, DirectoryFoodUserCreateSerializer, DirectoryIngredientsCreateSerializer, RecipeFoodCreateSerializer, \
     UserFoodDayDeleteSerializer, DirectoryFoodUserDeleteSerializer, DirectoryIngredientsDeleteSerializer

CONFIG = dotenv_values(".env")

class UserLoginView(LoginView):
    """Представление страницы авторизации"""
    model = UserBase
    success_url = '/'

class UserLogoutView(LogoutView):
    """Представление выхода авторизованного пользователя"""
    model = UserBase

class UserRegisterView(CreateAPIView):
    """Представление регистрации пользователя"""
    queryset = UserBase.objects.all()
    serializer_class = UserRegisterSerializer

class FoodSearchView(APIView):
    """Представление поиска еды для авторизованного пользователя."""
    serializer_class = SearchFoodSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @swagger_auto_schema(query_serializer=SearchQueryParamSerializer, 
                            manual_parameters=[openapi.Parameter(name='name', in_=openapi.IN_QUERY,
                            description='Name of food',
                            type=openapi.TYPE_STRING,
                            required=True), openapi.Parameter(name='lang', in_=openapi.IN_QUERY,
                            description='Language',
                            type=openapi.TYPE_STRING,
                            required=True)])
    def get(self, request):
        name_food = request.query_params['name']
        lang = request.query_params['lang']
        result = DirectoryFood.objects.filter(Q(name__icontains = name_food))
        if not len(result):
            req_result = requests.get(f'https://dietagram.p.rapidapi.com/apiFood.php?name={name_food}&lang={lang}', \
                headers= {'X-RapidAPI-Key': CONFIG['X-RapidAPI-Key'], 'X-RapidAPI-Host': CONFIG['X-RapidAPI-Host']})
            if req_result.status_code != HTTPStatus.OK:
                return Response({'error': 'Food not found'}, status=HTTPStatus.NOT_FOUND)
            else:
                data = req_result.json()
                if not len(data['dishes']):
                    return Response({'error': 'Food not found'}, status=HTTPStatus.NOT_FOUND)
                for i in data['dishes']:
                    try:
                        i_format = self.item_parse(i)
                        food_dir = DirectoryFood(name=i_format['name'], caloric=i_format['caloric'], fat=i_format['fat'],\
                             carbon=i_format['carbon'], protein=i_format['protein'])
                        food_dir.save()
                    except IntegrityError:
                        continue
                result = DirectoryFood.objects.filter(Q(name__icontains = name_food))
                return Response(SearchFoodSerializer(result, many=True).data)
        return Response(SearchFoodSerializer(result, many=True).data)

    def item_parse(self, item):
        result = {}
        for i in item.items():
            if i[0] in ('caloric', 'fat', 'carbon', 'protein'):
                format_float = i[1].replace(',', '.')
                result[i[0]] = int(float(format_float))
            else:
                result[i[0]] = i[1]
        return result

class UserFoodAddView(CreateAPIView):
    """Представление добавления пользовательской еды."""
    queryset = UserFoodDay.objects.all()
    serializer_class = UserFoodDaySerializer

class UserFoodDeleteView(DestroyAPIView):
    """Представление добавления пользовательской еды."""
    queryset = UserFoodDay.objects.all()
    serializer_class = UserFoodDayDeleteSerializer

class UserStatAddView(APIView):
    """Представление добавления количества калорий за день."""
    model = UserStat
    serializer_class= UserStatAddSerializer

    @swagger_auto_schema(
                            request_body=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                required= ['user', 'calories_burned'],
                                properties=  {
                                    'user' : openapi.Schema(type=openapi.TYPE_INTEGER), 
                                    'calories_burned' : openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'date': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            ))
    def post(self, request):
        stat = UserStat.objects.filter(user=UserBase.objects.get(id=request.data['user']), date=request.data['date'])
        if len(stat):
            result = UserStat.objects.get(user=UserBase.objects.get(id=request.data['user']), date=request.data['date'])
            result.calories_burned += request.data['calories_burned']
            result.save()
            return Response(UserStatAddSerializer(result, many=False).data)
        else:
            result = UserStat.objects.create(user=UserBase.objects.get(id=request.data['user']), calories_burned=request.data['calories_burned'])
            return Response(UserStatAddSerializer(result, many=False).data)

class DirectoryFoodUserCreateView(CreateAPIView):
    model = DirectoryFood
    serializer_class = DirectoryFoodUserCreateSerializer

class DirectoryFoodUserDeleteView(DestroyAPIView):
    model = DirectoryFood
    serializer_class = DirectoryFoodUserDeleteSerializer

class DirectoryIngredientsCreateView(CreateAPIView):
    model = DirectoryIngredients
    serializer_class = DirectoryIngredientsCreateSerializer

class DirectoryIngredientsDeleteView(DestroyAPIView):
    model = DirectoryIngredients
    serializer_class = DirectoryIngredientsDeleteSerializer

class RecipeCreateView(APIView):
    model = RecipeFood
    serializer_class = RecipeFoodCreateSerializer

    @swagger_auto_schema(
                            request_body=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                required= ['food', 'ingredients', 'user'],
                                properties=  {
                                    'user': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'food' : openapi.Schema(type=openapi.TYPE_STRING), 
                                    'ingredients': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, 
                                    required= ['ingredient', 'gram'],
                                        properties={  
                                        'ingredient': openapi.Schema(type=openapi.TYPE_STRING),  
                                        'gram': openapi.Schema(type=openapi.TYPE_INTEGER)}
                                    )
                                        
                                        )
                                        }
                                    ))
    def post(self, request):
        try:
            food = DirectoryFood.objects.get(name=request.data['food'])
            return Response({'error': 'product was created previously'}, status=HTTPStatus.NOT_FOUND)
        except DirectoryFood.DoesNotExist:
            food = DirectoryFood.objects.create(name=request.data['food'], user_create=UserBase.objects.get(id=request.data['user']))
            for ingredient in request.data['ingredients']:
                try:
                    ing = DirectoryIngredients.objects.get(name=ingredient['ingredient'])
                    RecipeFood.objects.create(food=food, ingredient=ing)
                    food.caloric += ing.caloric * (ingredient['gram'] * 0.01)
                    food.fat += ing.fat * (ingredient['gram'] * 0.01)
                    food.protein += ing.protein * (ingredient['gram'] * 0.01)
                    food.carbon += ing.carbon * (ingredient['gram'] * 0.01)
                    food.save()
                    return Response({'success': 'recipe create'}, status=HTTPStatus.CREATED)
                except DirectoryIngredients.DoesNotExist:
                    return Response({'error': 'ingredient not found'}, status=HTTPStatus.NOT_FOUND)
            
