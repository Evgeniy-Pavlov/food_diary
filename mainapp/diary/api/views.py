"""Модуль представлений django приложения."""
import io
import csv
from http import HTTPStatus
import requests
from dotenv import dotenv_values
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab import rl_config
from reportlab.platypus import Table, SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import HttpResponse, FileResponse
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from diary.models import UserBase, DirectoryFood, UserFoodDay, UserStat,\
    DirectoryIngredients, RecipeFood
from mainapp.settings import BASE_DIR
from .serializers import UserRegisterSerializer, SearchFoodSerializer,\
    SearchQueryParamSerializer, UserFoodDaySerializer, UserStatAddSerializer,\
    DirectoryFoodUserCreateSerializer, DirectoryIngredientsCreateSerializer,\
    RecipeFoodCreateSerializer, UserFoodDayDeleteSerializer, DirectoryFoodUserDeleteSerializer,\
    DirectoryIngredientsDeleteSerializer, UserStatForDaySerializer, \
    UserStatForDayQueryParamSerializer, RecipeFoodDeleteSerializer,\
    UserStatForPeriodQueryParamSerializer, UserStatForPeriodSerializer, \
    UserFoodDayAddSerializer, UserChangePwdSerializer, UserGetInfoSerializer,\
    UserGetInfoQueryParamSerializer, RecipeGetQueryParamSerializer

CONFIG = dotenv_values(".env")


styles = getSampleStyleSheet()

styles['Normal'].fontName='Arimo'
styles['Heading1'].fontName = 'Arimo'
rl_config.TTFSearchPath.append(str(BASE_DIR) + '/mainapp/font')
pdfmetrics.registerFont(TTFont('Arimo', 'Arimo-VariableFont_wght.ttf'))


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


class UserChangePasswordView(UpdateAPIView):
    """Представление изменения пароля учетной записи."""
    queryset = UserBase.objects.all()
    serializer_class = UserChangePwdSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def update(self, request, pk):
        user = UserBase.objects.get(username = request.data['username'])
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"error": ["old_password - Wrong password."]},\
                    status=HTTPStatus.BAD_REQUEST)
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response({'success': 'Password change'}, status=HTTPStatus.OK)
        return Response({"error": "Form is not valid"}, status=HTTPStatus.BAD_REQUEST)


class UserGetInfoView(APIView):
    """Представление получения информации о пользователе."""
    model = UserBase
    serializer_class = UserGetInfoSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


    @swagger_auto_schema(query_serializer=UserGetInfoQueryParamSerializer, \
        manual_parameters=[openapi.Parameter(name='username', in_=openapi.IN_QUERY, \
        description='Username', type=openapi.TYPE_STRING, required=True)])
    def get(self, request):
        """Реализация GET метода класса получения информации о пользователе."""
        try:
            user = UserBase.objects.get(username=request.query_params['username'])
            return Response(UserGetInfoSerializer(user, many=False).data)
        except UserBase.DoesNotExist:
            return Response({'error': 'Username not found'}, status=HTTPStatus.NOT_FOUND)


class FoodSearchView(APIView):
    """Представление поиска еды для авторизованного пользователя."""
    serializer_class = SearchFoodSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @swagger_auto_schema(query_serializer=SearchQueryParamSerializer, \
        manual_parameters=[openapi.Parameter(name='name', \
        in_=openapi.IN_QUERY, description='Name of food', \
        type=openapi.TYPE_STRING, required=True), \
        openapi.Parameter(name='lang', in_=openapi.IN_QUERY, \
        description='Language', type=openapi.TYPE_STRING, \
        required=True)])
    def get(self, request):
        """Реализация GET метода класса поиска еды.
        Условия следующие: Если запрашиваемая еда есть в БД,
        то возвращаем его. Если еды нет, то обращаемся
        к API DietaGram, результаты записываем в БД и возвращаем
        результат пользователю."""
        name_food = request.query_params['name']
        lang = request.query_params['lang']
        result = DirectoryFood.objects.filter(Q(name__icontains = name_food))
        if not len(result):
            req_result = requests.get(\
                f'https://dietagram.p.rapidapi.com/apiFood.php?name={name_food}&lang={lang}', \
                headers= {'X-RapidAPI-Key': CONFIG['X-RapidAPI-Key'],\
                    'X-RapidAPI-Host': CONFIG['X-RapidAPI-Host']})
            if req_result.status_code != HTTPStatus.OK:
                return Response({'error': 'Food not found'}, status=HTTPStatus.NOT_FOUND)
            else:
                data = req_result.json()
                if not len(data['dishes']):
                    return Response({'error': 'Food not found'}, status=HTTPStatus.NOT_FOUND)
                for i in data['dishes']:
                    try:
                        i_format = self.item_parse(i)
                        food_dir = DirectoryFood(name=i_format['name'],\
                            caloric=i_format['caloric'], fat=i_format['fat'],\
                            carbon=i_format['carbon'], protein=i_format['protein'])
                        food_dir.save()
                    except IntegrityError:
                        continue
                result = DirectoryFood.objects.filter(Q(name__icontains = name_food))
                return Response(SearchFoodSerializer(result, many=True).data)
        return Response(SearchFoodSerializer(result, many=True).data)

    def item_parse(self, item):
        """Внутренний метод парсинга ответа от внешнего api."""
        result = {}
        for i in item.items():
            if i[0] in ('caloric', 'fat', 'carbon', 'protein'):
                format_float = i[1].replace(',', '.')
                result[i[0]] = int(float(format_float))
            else:
                result[i[0]] = i[1]
        return result


class UserFoodAddView(APIView):
    """Представление добавления пользовательской еды."""
    queryset = UserFoodDay
    serializer_class = UserFoodDayAddSerializer
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
                            request_body=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                required= ['user', 'food'],
                                properties=  {
                                    'user' : openapi.Schema(type=openapi.TYPE_INTEGER), 
                                    'food' : openapi.Schema(type=openapi.TYPE_INTEGER), 
                                    'date': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            ))
    def post(self, request):
        """Реализация метода POST для представления."""
        user = UserBase.objects.get(id=request.data['user'])
        food = DirectoryFood.objects.get(id=request.data['food'])
        date = request.data['date']
        UserFoodDay.objects.create(user=user, food=food, date=date)
        stat = UserStat.objects.filter(user=user, date=date)
        if len(stat):
            result = UserStat.objects.get(user=user, date=date)
            result.calories_burned += food.caloric
            result.fat_burned += food.fat
            result.protein_burned += food.protein
            result.carbon_burned += food.carbon
            result.save()
            return Response(UserStatAddSerializer(result, many=False).data)
        else:
            result = UserStat.objects.create(user=user, calories_burned=food.caloric,\
                fat_burned=food.fat, protein_burned=food.protein, carbon_burned=food.carbon)
            return Response(UserStatAddSerializer(result, many=False).data)


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

    @swagger_auto_schema(request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, required= ['user',\
            'calories_burned', 'fat_burned', 'protein_burned','carbon_burned'],
            properties=  {
            'user' : openapi.Schema(type=openapi.TYPE_INTEGER), 
            'calories_burned' : openapi.Schema(type=openapi.TYPE_INTEGER),
            'fat_burned': openapi.Schema(type=openapi.TYPE_INTEGER),
            'protein_burned': openapi.Schema(type=openapi.TYPE_INTEGER),
            'carbon_burned': openapi.Schema(type=openapi.TYPE_INTEGER),
            'date': openapi.Schema(type=openapi.TYPE_STRING),}))
    def post(self, request):
        """Реализация метода POST для представления."""
        stat = UserStat.objects.filter(user=UserBase.objects.get(id=request.data['user']),\
            date=request.data['date'])
        if len(stat):
            result = UserStat.objects.get(user=UserBase.objects.get(id=request.data['user']),\
                date=request.data['date'])
            result.calories_burned += request.data['calories_burned']
            result.fat_burned += request.data['fat_burned']
            result.protein_burned += request.data['protein_burned']
            result.carbon_burned += request.data['carbon_burned']
            result.save()
            return Response(UserStatAddSerializer(result, many=False).data)
        else:
            result = UserStat.objects.create(user=UserBase.objects.get(\
                id=request.data['user']), calories_burned=request.data['calories_burned'],
                fat_burned=request.data['fat_burned'],
                protein_burned=request.data['protein_burned'],
                carbon_burned=request.data['carbon_burned'])
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

    @swagger_auto_schema(request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT, required= ['food', 'ingredients', 'user'],
    properties=  {'user': openapi.Schema(type=openapi.TYPE_INTEGER),
                'food' : openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING), 
                'ingredients': openapi.Schema(type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT, 
                required= ['ingredient', 'gram'],
                properties={'ingredient': openapi.Schema(type=openapi.TYPE_STRING),
                'gram': openapi.Schema(type=openapi.TYPE_INTEGER)}))}))
    def post(self, request):
        """Реализация метода POST для представления."""
        try:
            food = DirectoryFood.objects.get(name=request.data['food'])
            return Response({'error': 'product was created previously'},status=HTTPStatus.NOT_FOUND)
        except DirectoryFood.DoesNotExist:
            food = DirectoryFood.objects.create(name=request.data['food'],\
                user_create=UserBase.objects.get(id=request.data['user']),\
                description=request.data['description'])
            for ingredient in request.data['ingredients']:
                try:
                    ing = DirectoryIngredients.objects.get(name=ingredient['ingredient'])
                    RecipeFood.objects.create(food=food, ingredient=ing, gram=ingredient['gram'])
                    food.caloric += ing.caloric * (ingredient['gram'] * 0.01)
                    food.fat += ing.fat * (ingredient['gram'] * 0.01)
                    food.protein += ing.protein * (ingredient['gram'] * 0.01)
                    food.carbon += ing.carbon * (ingredient['gram'] * 0.01)
                    food.save()
                except DirectoryIngredients.DoesNotExist:
                    return Response({'error': 'ingredient not found'}, status=HTTPStatus.NOT_FOUND)
            return Response({'success': 'recipe create'}, status=HTTPStatus.CREATED)

class RecipeDeleteView(DestroyAPIView):
    """Представление удаления рецепта."""
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
            type=openapi.TYPE_STRING, required=True), 
            openapi.Parameter(name='user', in_=openapi.IN_QUERY,
            description='User id', type=openapi.TYPE_INTEGER, required=True)])
    def get(self, request):
        """Реализация GET метода класса получения статистики за день."""
        try:
            result = UserStat.objects.get(date=request.query_params['date'],\
                user=UserBase.objects.get(id=request.query_params['user']))
            return Response(UserStatForDaySerializer(result, many=False).data)
        except UserStat.DoesNotExist:
            return Response({"user": request.query_params['user'],\
                "date": request.query_params['date'], "calories_burned": 0},\
                status=HTTPStatus.NOT_FOUND)


class UserGetStatForPeriodView(APIView):
    """Получение статистики пользователя за период."""
    model = UserStat
    serializer_class = UserStatForPeriodSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @swagger_auto_schema(query_serializer=UserStatForPeriodQueryParamSerializer, 
            manual_parameters=[openapi.Parameter(name='date_start', in_=openapi.IN_QUERY,
            description='Start DateField for get stat on how much user eat',
            type=openapi.TYPE_STRING, required=True), 
            openapi.Parameter(name='date_end', in_=openapi.IN_QUERY,
            description='End DateField for get stat on how much user eat',
            type=openapi.TYPE_STRING, required=True), 
            openapi.Parameter(name='user', in_=openapi.IN_QUERY,
            description='User id', type=openapi.TYPE_INTEGER,
            required=True), openapi.Parameter(name='csv_file', in_=openapi.IN_QUERY,
            description='return csv file', type=openapi.TYPE_BOOLEAN,
            required=False), openapi.Parameter(name='pdf_file', in_=openapi.IN_QUERY,
            description='return pdf file', type=openapi.TYPE_BOOLEAN, required=False)])
    def get(self, request):
        """Реализация GET метода класса получения статистики за период."""
        result = UserStat.objects.filter(date__range=(request.query_params['date_start'],\
            request.query_params['date_end']),
            user=UserBase.objects.get(id=request.query_params['user']))
        start_date = request.query_params['date_start']
        date_end = request.query_params['date_end']
        if 'csv_file' in request.query_params and request.query_params['csv_file'] == 'true':
            response = HttpResponse(content_type="text/csv", \
                headers={"Content-Disposition": f'attachment; filename="calories_stat_for\
                _period_{start_date}-{date_end}.csv"'},)
            writer = csv.writer(response)
            writer.writerow(['id', 'user', 'date', 'calories_burned',\
                'fat_burned', 'protein_burned', 'carbon_birned'])
            for i in result:
                writer.writerow([i.id, i.user, i.date, i.calories_burned,\
                    i.fat_burned, i.protein_burned, i.carbon_burned])
            return response
        elif 'pdf_file' in request.query_params and request.query_params['pdf_file'] == 'true':
            buf = io.BytesIO()
            story = []
            title=f'Your report on calories/fat/protein/carbon \
                received the period from {start_date} to {date_end}'
            story.append(Paragraph(title, styles['Normal']))
            data = [('id', 'username', 'data', 'calories', 'fat', 'protein', 'carbon')]
            for i in result:
                data.append((i.id, i.user, i.date, i.calories_burned,\
                    i.fat_burned, i.protein_burned, i.carbon_burned))
            doc = SimpleDocTemplate(buf, rightMargin=0,\
                leftMargin=6.5, topMargin=0.3, bottomMargin=0)
            table = Table(data, hAlign='CENTER')
            story.append(table)
            doc.build(story)
            buf.seek(0)
            return FileResponse(buf, as_attachment=True, \
                filename=f'calories_stat_for_period_{start_date}-{date_end}.pdf')
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
                type=openapi.TYPE_STRING, required=True), 
                openapi.Parameter(name='user', in_=openapi.IN_QUERY,
                description='User id', type=openapi.TYPE_INTEGER, required=True)])
    def get(self, request):
        """Реализация GET метода класса получения блюд пользователя за день."""
        result = UserFoodDay.objects.filter(date=request.query_params['date'],\
            user=UserBase.objects.get(id=request.query_params['user']))\
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
            type=openapi.TYPE_STRING, required=True), 
            openapi.Parameter(name='date_end', in_=openapi.IN_QUERY,
            description='End DateField for get stat on how much user eat',
            type=openapi.TYPE_STRING, required=True), 
            openapi.Parameter(name='user', in_=openapi.IN_QUERY,
            description='User id', type=openapi.TYPE_INTEGER, required=True), 
            openapi.Parameter(name='csv_file', in_=openapi.IN_QUERY,
            description='return csv file', type=openapi.TYPE_BOOLEAN, required=False), 
            openapi.Parameter(name='pdf_file', in_=openapi.IN_QUERY,
            description='return pdf file',
            type=openapi.TYPE_BOOLEAN, required=False)])
    def get(self, request):
        """Реализация GET метода класса получения блюд пользователя за период."""
        result = UserFoodDay.objects.filter(date__range=(request.query_params['date_start'],\
            request.query_params['date_end']),
         user=UserBase.objects.get(id=request.query_params['user'])).select_related('food')
        start_date = request.query_params['date_start']
        date_end = request.query_params['date_end']
        if 'csv_file' in request.query_params and request.query_params['csv_file'] == 'true':
            response = HttpResponse(content_type="text/csv", \
                headers={"Content-Disposition": f'attachment; filename="userfoodday_stat_for\
                _period_{start_date}-{date_end}.csv"'},)
            writer = csv.writer(response)
            writer.writerow(['id', 'food id', 'username', 'date', 'name of food', 'caloric',\
                'fat', 'protein', 'carbon'])
            for i in result:
                writer.writerow([i.id, i.food.id, i.user, i.date, i.food.name, i.food.caloric,\
                    i.food.fat, i.food.protein, i.food.carbon])
            return response
        elif 'pdf_file' in request.query_params and request.query_params['pdf_file'] == 'true':
            buf = io.BytesIO()
            story = []
            data = [('id', 'food id', 'user id', 'date', 'food name', 'caloric', 'fat',\
                'protein', 'carbon')]
            for i in result:
                data.append((i.id, i.food, i.user, i.date,  Paragraph(i.food.name,\
                    styles['Normal']), i.food.caloric, i.food.fat, i.food.protein, i.food.carbon))
            doc = SimpleDocTemplate(buf, rightMargin=0, leftMargin=6.5,\
                topMargin=0.3, bottomMargin=0,)
            title=f'Your report on dishes eaten during the period from {start_date} to {date_end}'
            table = Table(data, hAlign='CENTER')
            story.append(Paragraph(title, styles['Normal']))
            story.append(table)
            doc.build(story)
            buf.seek(0)
            return FileResponse(buf, as_attachment=True,\
                filename=f'food_stat_for_period_{start_date}-{date_end}.pdf')
        else:
            return Response(UserFoodDaySerializer(result, many=True).data)


class FoodGetRecipeView(APIView):
    """Представление получения рецепта."""
    model = RecipeFood
    serializer_class = RecipeFoodCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @swagger_auto_schema(query_serializer= RecipeGetQueryParamSerializer,
                            manual_parameters=[openapi.Parameter(name='name', in_=openapi.IN_QUERY,
                            description='Name food',
                            type=openapi.TYPE_STRING,
                            required=True), openapi.Parameter(name='pdf_file', in_=openapi.IN_QUERY,
                            description='Recipe download pdf_file',
                            type=openapi.TYPE_BOOLEAN,
                            required=False)])
    def get(self, request):
        """Реализация GET метода класса получения рецепта."""
        food = DirectoryFood.objects.get(name=request.query_params['name'])
        ingredients = RecipeFood.objects.filter(food=food)
        if len(ingredients):
            result = {'food': food.name, 'recipe': food.description, 'ingredients': []}
            for ing in ingredients:
                item = {'ingredient name': ing.ingredient.name, 'gram': ing.gram}
                result['ingredients'].append(item)
            if 'pdf_file' in request.query_params and request.query_params['pdf_file'] == 'true':
                buf = io.BytesIO()
                story = []
                doc = SimpleDocTemplate(buf, rightMargin=0, leftMargin=6.5,\
                    topMargin=0.3, bottomMargin=0,)
                title=f'Recipe of {food.name}'
                story.append(Paragraph(title, styles['Normal']))
                story.append(Paragraph(result['recipe'], styles['Normal'])) if result['recipe']\
                    else story.append(Paragraph('Not description', styles['Normal']))
                table_data = [('ingredient', 'gram')]
                for i in result['ingredients']:
                    table_data.append((Paragraph(i['ingredient name'],\
                        styles['Normal']), i['gram']))
                table = Table(table_data, hAlign='CENTER')
                story.append(table)
                doc.build(story)
                buf.seek(0)
                return FileResponse(buf, as_attachment=True, filename=f'recipe_{food.name}.pdf')
            else:
                return Response(result, status=HTTPStatus.OK)
        else:
            return Response({'error': 'this food not have recipe'}, status=HTTPStatus.NOT_FOUND)

class RecipeUpdateView(APIView):
    """Представление обновления рецепта."""
    model = RecipeFood
    serializer_class = RecipeFoodCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @swagger_auto_schema(request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT, required= ['food', 'ingredients', 'user'],
    properties=  {'user': openapi.Schema(type=openapi.TYPE_INTEGER),
                'food' : openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING), 
                'ingredients': openapi.Schema(type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT, 
                required= ['ingredient', 'gram'],
                properties={'ingredient': openapi.Schema(type=openapi.TYPE_STRING),
                'gram': openapi.Schema(type=openapi.TYPE_INTEGER)}))}))
    def post(self, request):
        """Реализация метода POST для представления."""
        try:
            food = DirectoryFood.objects.get(name=request.data['food'])
            if 'description' in request.data:
                food.description = request.data['description']
            ingredients = RecipeFood.objects.filter(food=food)
            for ingredient in request.data['ingredients']:
                try:
                    ing = DirectoryIngredients.objects.get(name=ingredient['ingredient'])
                except DirectoryIngredients.DoesNotExist:
                    return Response({'error': 'ingredient not found'},status=HTTPStatus.NOT_FOUND)
            ingredients.delete()
            for ingredient in request.data['ingredients']:
                ing = DirectoryIngredients.objects.get(name=ingredient['ingredient'])
                RecipeFood.objects.create(food=food, ingredient=ing, gram=ingredient['gram'])
                food.caloric += ing.caloric * (ingredient['gram'] * 0.01)
                food.fat += ing.fat * (ingredient['gram'] * 0.01)
                food.protein += ing.protein * (ingredient['gram'] * 0.01)
                food.carbon += ing.carbon * (ingredient['gram'] * 0.01)
                food.save()
                return Response({'success': 'recipe create'}, status=HTTPStatus.CREATED)
        except DirectoryFood.DoesNotExist:
            return Response({'error': 'food not found'},status=HTTPStatus.NOT_FOUND)
            
