from rest_framework import serializers
from django.contrib.auth.models import User, Group

class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username','first_name', 'password', 'last_name', 'email', 'date_joined', 'is_staff', 'groups')


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'password', 'email')

    def create(self, validated_data):
        username = validated_data['username']
        first_name = validated_data['first_name'] 
        last_name = validated_data['last_name'] 
        email = validated_data['email']
        password = validated_data['password']

        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)

        group, _ = Group.objects.get_or_create(name="default_team")

        # Agregar el usuario al grupo
        user.groups.add(group)

        return user