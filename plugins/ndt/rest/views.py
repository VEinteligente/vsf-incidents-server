from rest_framework.authentication import BasicAuthentication
from vsf.vsf_authentication import VSFTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .serializers import (
    NDTSerializer,
    NDTFilter,
    DailyTestFilter,
    DailyTestSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from plugins.ndt.models import NDT, DailyTest


class ListNDT(generics.ListAPIView):

    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = NDT.objects.all()
    serializer_class = NDTSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = NDTFilter


class ListDailyTest(generics.ListAPIView):

    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = DailyTest.objects.all()
    serializer_class = DailyTestSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = DailyTestFilter
