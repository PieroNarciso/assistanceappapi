from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate

from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import authentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import exceptions

import random

from . import serializers
from . import models
from .utils import UserHandler


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permissions_classes = [permissions.IsAdminUser]
    authentication_classes = [authentication.TokenAuthentication]


class GetUserView(views.APIView):
    permissions_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request, *args, **kwargs):
        user = request.user
        res = UserHandler().get_user_data(user)
        return Response(res, status=200)


class NumCodeViewSet(viewsets.ModelViewSet):
    queryset = models.NumCode.objects.all()
    serializer_class = serializers.NumCodeSerializer
    permissions_classes = [permissions.IsAdminUser]
    authentication_classes = [authentication.TokenAuthentication]

    def create(self, request, *args, **kwargs):
        code = models.NumCode(code=random.randint(100000, 999999))
        models.NumCode.objects.all().exclude(pk=code.pk).delete()
        serializer = self.serializer_class(code, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class NumCodeLastView(views.APIView):
    permissions_classes = [permissions.IsAdminUser]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request, *args, **kwargs):
        code = models.NumCode.objects.last().code
        return Response({'code': code}, status=200)


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
