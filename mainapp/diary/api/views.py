import os
import io
import csv
from http import HTTPStatus
import requests
from dotenv import dotenv_values
from drf_yasg import openapi
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse, FileResponse
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from diary.models import UserBase, DirectoryFood, UserFoodDay, UserStat, DirectoryIngredients, RecipeFood
from django.db.utils import IntegrityError
from .serializers import UserRegisterSerializer, SearchFoodSerializer, SearchQueryParamSerializer, UserFoodDaySerializer, \
     UserStatAddSerializer, DirectoryFoodUserCreateSerializer, DirectoryIngredientsCreateSerializer, RecipeFoodCreateSerializer, \
     UserFoodDayDeleteSerializer, DirectoryFoodUserDeleteSerializer, DirectoryIngredientsDeleteSerializer, UserStatForDaySerializer, \
     UserStatForDayQueryParamSerializer, RecipeFoodDeleteSerializer, UserStatForPeriodQueryParamSerializer, UserStatForPeriodSerializer, \
     UserFoodDayAddSerializer \

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
    serializer_class = UserFoodDayAddSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class UserFoodDeleteView(DestroyAPIView):
    """Представление добавления пользовательской еды."""
    queryset = UserFoodDay.objects.all()
    serializer_class = UserFoodDayDeleteSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class UserStatAddView(APIView):
    """Представление добавления количества калорий за день."""
    model = UserStat
    serializer_class= UserStatAddSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

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
    """Представление создания блюда в справочник еды"""
    model = DirectoryFood
    serializer_class = DirectoryFoodUserCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class DirectoryFoodUserDeleteView(DestroyAPIView):
    """Представление удаления блюда из справочника еды"""
    queryset = DirectoryFood.objects.all()
    serializer_class = DirectoryFoodUserDeleteSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class DirectoryIngredientsCreateView(CreateAPIView):
    """Представление добавления ингредиента в справочник ингредиентов"""
    model = DirectoryIngredients
    serializer_class = DirectoryIngredientsCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class DirectoryIngredientsDeleteView(DestroyAPIView):
    """Предстваление удаления ингредиента из справочника ингредиентов"""
    queryset = DirectoryIngredients.objects.all()
    serializer_class = DirectoryIngredientsDeleteSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class RecipeCreateView(APIView):
    """Представление создания рецепта"""
    model = RecipeFood
    serializer_class = RecipeFoodCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

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

class RecipeDeleteView(DestroyAPIView):
    queryset = RecipeFood.objects.all()
    serializer_class = RecipeFoodDeleteSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class UserGetStatForDayView(APIView):
    """Получение статистики пользователя за конкретный день."""
    model = UserStat
    serializer_class = UserStatForDaySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @swagger_auto_schema(query_serializer=UserStatForDayQueryParamSerializer, 
                            manual_parameters=[openapi.Parameter(name='date', in_=openapi.IN_QUERY,
                            description='DateField for get stat on how much user eat',
                            type=openapi.TYPE_STRING,
                            required=True), openapi.Parameter(name='user', in_=openapi.IN_QUERY,
                            description='User id',
                            type=openapi.TYPE_INTEGER,
                            required=True)])
    def get(self, request):
        try:
            result = UserStat.objects.get(date=request.query_params['date'], user=UserBase.objects.get(id=request.query_params['user']))
            return Response(UserStatForDaySerializer(result, many=False).data)
        except UserStat.DoesNotExist:
            return Response({"user": request.query_params['user'], "date": request.query_params['date'], "calories_burned": 0}, status=HTTPStatus.NOT_FOUND)


class UserGetStatForPeriodView(APIView):
    """Получение статистики пользователя за период."""
    model = UserStat
    serializer_class = UserStatForPeriodSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @swagger_auto_schema(query_serializer=UserStatForPeriodQueryParamSerializer, 
                            manual_parameters=[openapi.Parameter(name='date_start', in_=openapi.IN_QUERY,
                            description='Start DateField for get stat on how much user eat',
                            type=openapi.TYPE_STRING,
                            required=True), openapi.Parameter(name='date_end', in_=openapi.IN_QUERY,
                            description='End DateField for get stat on how much user eat',
                            type=openapi.TYPE_STRING,
                            required=True), openapi.Parameter(name='user', in_=openapi.IN_QUERY,
                            description='User id',
                            type=openapi.TYPE_INTEGER,
                            required=True), openapi.Parameter(name='csv_file', in_=openapi.IN_QUERY,
                            description='return csv file',
                            type=openapi.TYPE_BOOLEAN,
                            required=False), openapi.Parameter(name='pdf_file', in_=openapi.IN_QUERY,
                            description='return pdf file',
                            type=openapi.TYPE_BOOLEAN,
                            required=False)])
    def get(self, request):
        result = UserStat.objects.filter(date__range=(request.query_params['date_start'], request.query_params['date_end']),
            user=UserBase.objects.get(id=request.query_params['user']))
        start_date = request.query_params['date_start']
        date_end = request.query_params['date_end']
        if 'csv_file' in request.query_params and request.query_params['csv_file'] == 'true':
            response = HttpResponse(content_type="text/csv", headers={"Content-Disposition": f'attachment; filename="calories_stat_for\
            _period_{start_date}-{date_end}.csv"'},)
            writer = csv.writer(response)
            writer.writerow(['id', 'user', 'date', 'calories_burned'])
            for i in result:
                writer.writerow([i.id, i.user, i.date, i.calories_burned])
            return response
        elif 'pdf_file' in request.query_params and request.query_params['pdf_file'] == 'true':
            buf = io.BytesIO()
            canv = canvas.Canvas(buf, pagesize=letter, bottomup=0)
            textob = canv.beginText()
            textob.setTextOrigin(inch, inch)
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            textob.setFont('Arial', 14)
            textob.textLine(f'Your calorie report for the period from {start_date} to {date_end}')
            textob.textLine(f'id | user_id | date | callories')
            for i in result:
                textob.textLine(f'{i.id} | {i.user} | {i.date} | {i.calories_burned}')
            canv.drawText(textob)
            canv.showPage()
            canv.save()
            buf.seek(0)
            return FileResponse(buf, as_attachment=True, filename=f'calories_stat_for_period_{start_date}-{date_end}.pdf')
        else:
            return Response(UserStatForPeriodSerializer(result, many=True).data)


class UserFoodDayStatView(APIView):
    """Представление получения блюд пользователя за день."""
    model = UserFoodDay
    serializer_class = UserFoodDaySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @swagger_auto_schema(query_serializer=UserStatForDayQueryParamSerializer, 
                            manual_parameters=[openapi.Parameter(name='date', in_=openapi.IN_QUERY,
                            description='DateField for get stat on how much user eat',
                            type=openapi.TYPE_STRING,
                            required=True), openapi.Parameter(name='user', in_=openapi.IN_QUERY,
                            description='User id',
                            type=openapi.TYPE_INTEGER,
                            required=True)])
    def get(self, request):
        result = UserFoodDay.objects.filter(date=request.query_params['date'], user=UserBase.objects.get(id=request.query_params['user']))\
            .select_related('food')
        return Response(UserFoodDaySerializer(result, many=True).data)


class UserFoodDayStatPeriodView(APIView):
    """Представление получения блюд пользователя за период."""
    model = UserFoodDay
    serializer_class = UserFoodDaySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @swagger_auto_schema(query_serializer=UserStatForPeriodQueryParamSerializer, 
                            manual_parameters=[openapi.Parameter(name='date_start', in_=openapi.IN_QUERY,
                            description='Start DateField for get stat on how much user eat',
                            type=openapi.TYPE_STRING,
                            required=True), openapi.Parameter(name='date_end', in_=openapi.IN_QUERY,
                            description='End DateField for get stat on how much user eat',
                            type=openapi.TYPE_STRING,
                            required=True), openapi.Parameter(name='user', in_=openapi.IN_QUERY,
                            description='User id',
                            type=openapi.TYPE_INTEGER,
                            required=True), openapi.Parameter(name='csv_file', in_=openapi.IN_QUERY,
                            description='return csv file',
                            type=openapi.TYPE_BOOLEAN,
                            required=False), openapi.Parameter(name='pdf_file', in_=openapi.IN_QUERY,
                            description='return pdf file',
                            type=openapi.TYPE_BOOLEAN,
                            required=False)])
    def get(self, request):
        result = UserFoodDay.objects.filter(date__range=(request.query_params['date_start'], request.query_params['date_end']),
         user=UserBase.objects.get(id=request.query_params['user'])).select_related('food')
        start_date = request.query_params['date_start']
        date_end = request.query_params['date_end']
        if 'csv_file' in request.query_params and request.query_params['csv_file'] == 'true':
            response = HttpResponse(content_type="text/csv", headers={"Content-Disposition": f'attachment; filename="userfoodday_stat_for\
            _period_{start_date}-{date_end}.csv"'},)
            writer = csv.writer(response)
            writer.writerow(['id', 'food id', 'username', 'date', 'name of food', 'caloric', 'fat', 'protein', 'carbon'])
            for i in result:
                writer.writerow([i.id, i.food.id, i.user, i.date, i.food.name, i.food.caloric, i.food.fat, i.food.protein, i.food.carbon])
            return response
        elif 'pdf_file' in request.query_params and request.query_params['pdf_file'] == 'true':
            buf = io.BytesIO()
            canv = canvas.Canvas(buf, pagesize=letter, bottomup=0)
            textob = canv.beginText()
            textob.setTextOrigin(inch, inch)
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            textob.setFont('Arial', 14)
            textob.textLine(f'Your report on dishes eaten during the period from {start_date} to {date_end}')
            textob.textLine(f'id | food id | user id | date | food name | caloric | fat | protein | carbon')
            for i in result:
                textob.textLine(f'{i.id} | {i.food.id} | {i.user} | {i.date} | {i.food.name} | {i.food.caloric} | {i.food.fat} | {i.food.protein} | {i.food.carbon}')
            canv.drawText(textob)
            canv.showPage()
            canv.save()
            buf.seek(0)
            return FileResponse(buf, as_attachment=True, filename=f'food_stat_for_period_{start_date}-{date_end}.pdf')
        else:
            return Response(UserFoodDaySerializer(result, many=True).data)
