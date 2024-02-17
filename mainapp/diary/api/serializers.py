from rest_framework.serializers import ModelSerializer, CharField, DateField, IntegerField, BooleanField
from diary.models import UserBase, DirectoryFood, UserFoodDay, UserStat, DirectoryIngredients, RecipeFood

class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = UserBase
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = UserBase(username=validated_data['username'], email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserGetInfoSerializer(ModelSerializer):
    class Meta:
        model = UserBase
        fields = ('id', 'username', 'email')

class UserGetInfoQueryParamSerializer(ModelSerializer):
    username = CharField(required=True)
    
    class Meta:
        model = UserBase
        fields = ('username',)


class UserChangePwdSerializer(ModelSerializer):
    username = CharField(required=True)
    old_password = CharField(required=True)
    new_password = CharField(required=True)

    class Meta:
        model = UserBase
        fields = ('username', 'old_password', 'new_password')
        


class SearchFoodSerializer(ModelSerializer):
    class Meta:
        model = DirectoryFood
        fields = ('id', 'name', 'caloric', 'fat', 'carbon', 'protein')


class SearchQueryParamSerializer(ModelSerializer):
    name = CharField(help_text='Name of food', required=False)
    lang = CharField(help_text='Search language ', required=False)

    class Meta:
        model = DirectoryFood
        fields = ('name', 'lang')


class UserFoodDaySerializer(ModelSerializer):
    name = CharField(source='food.name')
    caloric = IntegerField(source='food.caloric')
    fat = IntegerField(source='food.fat')
    protein = IntegerField(source='food.protein')
    carbon = IntegerField(source='food.carbon')
    
    class Meta:
        model = UserFoodDay
        fields = ('id', 'food', 'user', 'date', 'name', 'caloric', 'fat', 'protein', 'carbon')


class UserFoodDayAddSerializer(ModelSerializer):
    class Meta:
        model = UserFoodDay
        fields = ('id', 'food', 'user', 'date')


class UserFoodDayDeleteSerializer(ModelSerializer):
    class Meta:
        model = UserFoodDay
        fields = ('id', 'food', 'date')


class UserStatAddSerializer(ModelSerializer):
    class Meta:
        model = UserStat
        fields = ('id', 'user', 'date', 'calories_burned')


class DirectoryFoodUserCreateSerializer(ModelSerializer):
    class Meta:
        model = DirectoryFood
        fields = ('id', 'name', 'caloric', 'fat', 'carbon', 'protein', 'user_create')


class DirectoryFoodUserDeleteSerializer(ModelSerializer):
    class Meta:
        model = DirectoryFood
        fields = ('id', 'name', 'caloric', 'fat', 'carbon', 'protein', 'user_create')


class DirectoryIngredientsCreateSerializer(ModelSerializer):
    class Meta:
        model = DirectoryIngredients
        fields = ('id', 'name', 'caloric', 'fat', 'carbon', 'protein', 'user_create')


class DirectoryIngredientsDeleteSerializer(ModelSerializer):
    class Meta:
        model = DirectoryIngredients
        fields = ('id', 'name')


class RecipeFoodCreateSerializer(ModelSerializer):
    class Meta:
        model = RecipeFood
        fields = ('food', 'ingredients', 'gram')


class UserStatForDaySerializer(ModelSerializer):
    class Meta:
        model = UserStat
        fields = ('id', 'user', 'date', 'calories_burned')


class UserStatForPeriodSerializer(ModelSerializer):
    class Meta:
        model = UserStat
        fields = ('id', 'user', 'date', 'calories_burned')


class UserStatForDayQueryParamSerializer(ModelSerializer):
    date = DateField(help_text='DateField for get stat on how much user eat', required=True)
    user = IntegerField(help_text='User id', required=True)

    class Meta:
        model = UserStat
        fields = ('date', 'user')


class UserStatForPeriodQueryParamSerializer(ModelSerializer):
    date_start = DateField(help_text='DateField for get stat on how much user eat', required=True)
    date_end = DateField(help_text='DateField for get stat on how much user eat', required=True)
    user = IntegerField(help_text='User id', required=True)
    csv_file = BooleanField(help_text='Return csv file', required=False)
    pdf_file = BooleanField(help_text='Return pdf file', required=False)

    class Meta:
        model = UserStat
        fields = ('date_start', 'date_end', 'user', 'csv_file', 'pdf_file')


class RecipeFoodDeleteSerializer(ModelSerializer):
    class Meta:
        model = RecipeFood
        fields = ('food', 'ingredients', 'gram')
