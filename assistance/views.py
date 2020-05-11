from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate

from rest_framework.decorators import action
from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import authentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import exceptions
from rest_framework import status

import pandas as pd

import random
from datetime import datetime
import sys

from assistance import serializers
from assistance import models
from assistance.utils import UserHandler


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def create(self, request, *args, **kwargs):
        """
        Create an `User instance` and save it to the database.

        Args:
            request.data: Data mapping the User data. For example:

                    data = {
                        'username': string type,
                        'first_name': string type,
                        'last_name': string type,
                        'password': string type ,
                        'email': string type
                    }

        Returns:
            Response object: User's serialized data in JSON.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'], authentication_classes=[authentication.TokenAuthentication])
    def get_user_data(self, request, *args, **kwargs):
        """
        Return a JSON response to the request with this structure
            result = {
                "user_id": integer type,
                "username": string type,
                "email": string type,
                "first_name": string type,
                "last_name": string type,
                "login": boolean type,
                "token": string type
            }

        The request must provide the `Token` of the user in the header
        """
        if request.user.is_authenticated:
            res = UserHandler().get_login_data(user=request.user)
            return Response(res, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class NumCodeViewSet(viewsets.ModelViewSet):
    queryset = models.NumCode.objects.all()
    serializer_class = serializers.NumCodeSerializer
    permissions_classes = [permissions.IsAdminUser]
    authentication_classes = [authentication.TokenAuthentication]

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        code = models.NumCode(code=random.randint(100000, 999999))
        serializer = self.serializer_class(code, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        if self.queryset.count() > 1:
            models.NumCode.objects.all().exclude(pk=code.pk).delete()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'], permission_classes=[permissions.IsAdminUser])
    def get_code(self, request, *args, **kwargs):
        code = self.queryset.last().code
        return Response({'code': code}, status=status.HTTP_200_OK)


class AssistanceViewSet(viewsets.ModelViewSet):
    queryset = models.Assistance.objects.all().order_by('check_time').reverse()
    serializer_class = serializers.AssistanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def create(self, request, *args, **kwargs):
        res = {
            'msg': 'Invalid code'
        }
        res_code = request.data.get('code')
        try:
            res_code = int(res_code)
        except ValueError:
            raise exceptions.ValidationError(res)
        code = models.NumCode.objects.last().code
        if res_code != code:
            raise exceptions.ValidationError(res)
        user = request.user
        assistance = models.Assistance(user=user)
        serializer = self.serializer_class(assistance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['GET'])
    def get_today(self, request, *args, **kwargs):
        date = datetime.today()
        queryset = models.Assistance.objects.filter(
            check_time__year=date.year, check_time__month=date.month, check_time__day=date.day)
        serializer = self.serializer_class(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def download_data(self, request, *args, **kwargs):
        date_range = request.data.get('date_range')
        if len(date_range) == 1 or date_range[0] == date_range[1]:
            queryset = models.Assistance.objects.filter(
                check_time__date=date_range[0])
        else:
            queryset = models.Assistance.objects.filter(
                check_time__range=date_range)
        serializer = self.serializer_class(instance=queryset, many=True)
        print(serializer.data)
        sys.stdout.flush()
        df = pd.DataFrame(serializer.data)
        print(df.to_csv(index=False))
        sys.stdout.flush()
        return Response(df.to_csv(index=False), status=status.HTTP_200_OK)


class CustomAuthToken(ObtainAuthToken):
    permissions_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        res = UserHandler().get_token_data(user, token)
        response = Response(res, status=200)
        response.set_cookie('token', token)
        return response
