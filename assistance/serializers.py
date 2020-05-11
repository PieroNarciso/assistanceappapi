from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate

from rest_framework import serializers
from rest_framework import exceptions
from rest_framework.authtoken.models import Token

from assistance import models


class NumCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NumCode
        fields = [
            'code'
        ]
        extra_kwargs = {
            'code': {
                'required': False
            }
        }


class AssistanceSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(many=False)

    class Meta:
        model = models.Assistance
        fields = [
            'id',
            'check_time',
            'user'
        ]
        extra_kwargs = {
            'user': {
                'required': False
            }
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        ]
        extra_kwargs = {
            'password': {
                'required': True,
                'write_only': True
            }
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = [
            'username',
            'password'
        ]

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)

        if not username and not password:
            raise exceptions.ValidationError("Email and password are required")

        user = authenticate(username=username, password=password)
        if user:
            data['user'] = user
        else:
            raise exceptions.ValidationError("Incorrect credentials.")
        return data
