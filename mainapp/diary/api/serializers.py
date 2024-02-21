"""Модуль сериализаторов представлений и query-параметров."""
from rest_framework.serializers import ModelSerializer, \
    CharField, DateField, IntegerField, BooleanField
from diary.models import UserBase, DirectoryFood, \
    UserFoodDay, UserStat, DirectoryIngredients, RecipeFood


class UserRegisterSerializer(ModelSerializer):
    """Сериализатор представления регистрации пользователя."""

    class Meta:
        """Метакласс сериализатора. Определяет поля
        username, email, password."""
        model = UserBase
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = UserBase(
            username=validated_data['username'], email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserGetInfoSerializer(ModelSerializer):
    """Сериализатор представления получения информации 
    о пользователе."""

    class Meta:
        """Метакласс сериализатора. Определяется поля
        id, username, email."""
        model = UserBase
        fields = ('id', 'username', 'email')


class UserGetInfoQueryParamSerializer(ModelSerializer):
    """Сериализатор query-параметров представления
    получения информации о пользователе."""
    username = CharField(required=True)

    class Meta:
        """Метакласс сериализатора. Определяется поле
        username"""
        model = UserBase
        fields = ('username',)


class RecipeGetQueryParamSerializer(ModelSerializer):
    """Сериализатор query-параметров представления
    получения рецепта."""
    name = CharField(required=True)

    class Meta:
        """Метакласс сериализатора. Определяется поле
        name."""
        model = DirectoryFood
        fields = ('name',)

class UserChangePwdSerializer(ModelSerializer):
    """Сериализатор представления изменения пароля."""
    username = CharField(required=True)
    old_password = CharField(required=True)
    new_password = CharField(required=True)

    class Meta:
        """Метакласс  сериализатора. Определяет поля
        username, old_password, new_password."""
        model = UserBase
        fields = ('username', 'old_password', 'new_password')

class SearchFoodSerializer(ModelSerializer):
    """Сериализатор представления поиска еды."""

    class Meta:
        """Метакласс сериазатора представления поиска еды."""
        model = DirectoryFood
        fields = ('id', 'name', 'caloric', 'fat', 'carbon', 'protein')


class SearchQueryParamSerializer(ModelSerializer):
    """Сериализатор query-параметров поиска еды."""
    name = CharField(help_text='Name of food', required=False)
    lang = CharField(help_text='Search language ', required=False)

    class Meta:
        """Метакласс сериализатора поиска еды.
        Определяет поля поиска name и lang."""
        model = DirectoryFood
        fields = ('name', 'lang')


class UserFoodDaySerializer(ModelSerializer):
    """Сериализатор представления получения статистики
    по еде за день."""
    name = CharField(source='food.name')
    caloric = IntegerField(source='food.caloric')
    fat = IntegerField(source='food.fat')
    protein = IntegerField(source='food.protein')
    carbon = IntegerField(source='food.carbon')

    class Meta:
        """Метакласс сериализатора. Определяет поля
        id, food, user, date, name, caloric,
        fat, protein, carbon."""
        model = UserFoodDay
        fields = ('id', 'food', 'user', 'date', 'name',
                  'caloric', 'fat', 'protein', 'carbon')


class UserFoodDayAddSerializer(ModelSerializer):
    """Сериазиатор представления добавления
    данных в статистику о еде пользователя за день."""

    class Meta:
        """Метакласс сериализатора. Определяет поля
        id, food, user, date."""
        model = UserFoodDay
        fields = ('id', 'food', 'user', 'date')


class UserFoodDayDeleteSerializer(ModelSerializer):
    """Сериализатор представления удаления
    данных из статистики о еде пользователя
    за день."""

    class Meta:
        """Метакласс сериализатора. Определяет
        поля id, food, date."""
        model = UserFoodDay
        fields = ('id', 'food', 'date')


class UserStatAddSerializer(ModelSerializer):
    """Сериализатор представления добавления
    статистики за день по калориям и БЖУ."""

    class Meta:
        """Метакласс сериализатора. Определяет поля
        id, user, date, calories_burned."""
        model = UserStat
        fields = ('id', 'user', 'date', 'calories_burned')


class DirectoryFoodUserCreateSerializer(ModelSerializer):
    """Сериализатор представления добавления
    еды в справочник блюд."""

    class Meta:
        """Метакласс сериализатора. Определяет поля
        id, name, caloric, fat, carbon, protein,
        user_create."""
        model = DirectoryFood
        fields = ('id', 'name', 'caloric', 'fat',
                  'carbon', 'protein', 'user_create')


class DirectoryFoodUserDeleteSerializer(ModelSerializer):
    """Сериализатор представления удаления еды из
    справочника блюд."""

    class Meta:
        """Метакласс сериализатора. Определяет поля
        id, name, caloric, fat, carbon, protein,
        user_create."""
        model = DirectoryFood
        fields = ('id', 'name', 'caloric', 'fat',
                  'carbon', 'protein', 'user_create')


class DirectoryIngredientsCreateSerializer(ModelSerializer):
    """Сериализатор представления добавления ингредиента 
    в справочник ингредиентов."""

    class Meta:
        """Метакласс сериализатора. Определяет поля
        id, name, caloric, fat, carbon, protein, user_create."""
        model = DirectoryIngredients
        fields = ('id', 'name', 'caloric', 'fat',
                  'carbon', 'protein', 'user_create')


class DirectoryIngredientsDeleteSerializer(ModelSerializer):
    """Сериализатор представления удаления ингредиентов
    в справочнике ингредиентов."""

    class Meta:
        """Метакласс сериализатора. Определяет поля
        id, name."""
        model = DirectoryIngredients
        fields = ('id', 'name')


class RecipeFoodCreateSerializer(ModelSerializer):
    """Сериализатор представления создания рецептов."""

    class Meta:
        """Метакласс сериализатора. Определяет поля
        food, ingrediets, gram."""
        model = RecipeFood
        fields = ('food', 'ingredients', 'gram')


class UserStatForDaySerializer(ModelSerializer):
    """Сериализатор представления добавления статистики
    пользователя за день."""

    class Meta:
        """Метакласс сериализатора. Определяет поля
        id, user, date, calories_burned, fat_burned,
        protein_burned, carbon_burned."""
        model = UserStat
        fields = ('id', 'user', 'date', 'calories_burned', 'fat_burned', \
            'protein_burned', 'carbon_burned')


class UserStatForPeriodSerializer(ModelSerializer):
    """Сериализатор представления получения статистики
    пользователя за период."""

    class Meta:
        """Метакласс сериализатора. Определяет поля
        id, user, date, calories_burned."""
        model = UserStat
        fields = ('id', 'user', 'date', 'calories_burned')


class UserStatForDayQueryParamSerializer(ModelSerializer):
    """Сериализатор query-параметров для представления
    получения статистики пользователя за день.."""
    date = DateField(
        help_text='DateField for get stat on how much user eat', required=True)
    user = IntegerField(help_text='User id', required=True)

    class Meta:
        """Метакласс сериализатора. Определяет поля
        date, user."""
        model = UserStat
        fields = ('date', 'user')


class UserStatForPeriodQueryParamSerializer(ModelSerializer):
    """Сериализатор query-параметров для представления получения
    статистики пользователя за период."""
    date_start = DateField(
        help_text='DateField for get stat on how much user eat', required=True)
    date_end = DateField(
        help_text='DateField for get stat on how much user eat', required=True)
    user = IntegerField(help_text='User id', required=True)
    csv_file = BooleanField(help_text='Return csv file', required=False)
    pdf_file = BooleanField(help_text='Return pdf file', required=False)

    class Meta:
        """Метакласс сериализатора. Определяет поля
        date_start, date_end, user, csv_file, pdf_file."""
        model = UserStat
        fields = ('date_start', 'date_end', 'user', 'csv_file', 'pdf_file')


class RecipeFoodDeleteSerializer(ModelSerializer):
    """Сериализатор представления удаления рецепта
    из справочника блюд."""

    class Meta:
        """Метакласс сериализатора. Определяет поля
        food, ingredients, gram"""
        model = RecipeFood
        fields = ('food', 'ingredients', 'gram')
