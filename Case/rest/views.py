from django.shortcuts import render
from rest_framework import generics, status, exceptions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from serializers import (
    DetailEventCaseSerializer,
    CaseSerializer
)
from Case.models import Case
from django.http import Http404


# Create your views here.

class DetailCaseRestView(APIView):

    permission_classes = (AllowAny,)

    def get_object(self, pk):
        try:
            return Case.objects.get(pk=pk)
        except Case.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        case = self.get_object(pk)
        serializer = CaseSerializer(case)
        return Response(serializer.data)


class DetailEventCaseRestView(APIView):

    permission_classes = (AllowAny,)

    def get_object(self, pk):
        try:
            return Case.objects.get(pk=pk)
        except Case.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        case = self.get_object(pk)
        serializer = DetailEventCaseSerializer(case)
        return Response(serializer.data)
