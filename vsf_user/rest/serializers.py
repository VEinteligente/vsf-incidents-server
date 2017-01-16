import json

from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from vsf_user.models import TokenControl


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ()


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        exclude = ()


class TokenControlSerializer(serializers.ModelSerializer):

    class Meta:
        model = TokenControl
        exclude = ('id',)


class ApiKeyUserSerializer(UserSerializer):
    token_control = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        exclude = ('password',)

    @staticmethod
    def get_token_control(obj):
        token = Token.objects.get(user=obj)
        return TokenControlSerializer(TokenControl.objects.get(token=token)).data
