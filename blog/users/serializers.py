from rest_framework import serializers
from django.contrib.auth.models import User, Group
from rest_framework.validators import UniqueValidator

class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username','password', 'date_joined', 'is_staff', 'groups')


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Este nombre de usuario ya está en  uso."
            )
        ]
    )
    class Meta:
        model = User
        fields = ('username','password')

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']

        user = User.objects.create_user(username=username, password=password)

        group, _ = Group.objects.get_or_create(name="default_team")

        user.groups.add(group)

        return user
    