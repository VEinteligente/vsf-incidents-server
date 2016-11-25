from django.shortcuts import render
from rest_framework import generics, status, exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from serializers import (
    DetailEventCaseSerializer,
    CaseSerializer
)
from Case.models import Case
from django.http import Http404


# Create your views here.

class DetailCaseRestView(generics.RetrieveAPIView):

    #authentication_classes = (TokenAuthentication, BasicAuthentication)
    #permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Case.objects.filter(draft=False)
    lookup_url_kwarg = 'case_id'
    serializer_class = CaseSerializer


class DetailEventCaseRestView(generics.RetrieveAPIView):

    #authentication_classes = (TokenAuthentication, BasicAuthentication)
    #permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Case.objects.filter(draft=False)
    lookup_url_kwarg = 'case_id'
    serializer_class = DetailEventCaseSerializer
