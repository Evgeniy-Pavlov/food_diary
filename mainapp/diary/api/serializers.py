from rest_framework.serializers import ModelSerializer, CharField
from diary.models import UserBase, DirectoryFood

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