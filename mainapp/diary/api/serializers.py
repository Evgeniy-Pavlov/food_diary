from rest_framework.serializers import ModelSerializer
from diary.models import UserBase

class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = UserBase
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = UserBase(username=validated_data['username'], email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user