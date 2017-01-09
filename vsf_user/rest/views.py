from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from vsf.vsf_authentication import VSFTokenAuthentication
from vsf_user.rest.serializers import ApiKeyUserSerializer


class DetailApiKeyUser(generics.RetrieveAPIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.filter(groups__name='api')
    lookup_url_kwarg = 'user_id'
    serializer_class = ApiKeyUserSerializer


class GenerateToken(APIView):
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        token = Token.objects.get(user=request.user)
        content = {
            'token': token.key
        }
        return Response(content)


class ExampleView(APIView):
    authentication_classes = (TokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': unicode(request.user),  # `django.contrib.auth.User` instance.
            'auth': unicode(request.auth),  # None
        }
        return Response(content)
