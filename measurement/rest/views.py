<<<<<<< HEAD
from rest_framework import generics
from rest_framework.permissions import AllowAny

from measurement.models import Metric
=======
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import generics

from measurement.rest import serializers
from measurement.models import Metric, Flag
from measurement.rest.serializers import FlagSerializer
>>>>>>> rest247

from serializers import (
    MeasurementSerializer,
    DNSMeasurementSerializer
)


class MeasurementRestView(generics.ListAPIView):
    """MeasurementRestView: APIView
    for displaying a list of measurements"""
    #   authentication_classes = (TokenAuthentication, BasicAuthentication)
    #   permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
<<<<<<< HEAD
    queryset = Metric.objects.all()
    serializer_class = MeasurementSerializer
=======

    def get(self, request):
        """List measurements"""
        serializer = serializers.MeasurementSerializer(
            Metric.objects.all().first())
        return Response(serializer.data)
>>>>>>> rest247


class DNSMeasurementRestView(generics.ListAPIView):
    """DNSMeasurementRestView: MeasurementRestView
    for displaying a list of DNS measurements"""
<<<<<<< HEAD
    permission_classes = (AllowAny,)
    queryset = Metric.objects.filter(test_name='dns_consistency')
    serializer_class = DNSMeasurementSerializer
=======

    def get(self, request):
        """List DNS measurements"""
        serializer = serializers.DNSMeasurementSerializer(
            Metric.objects.filter(test_name='dns_consistency').first())
        return Response(serializer.data)


class FlagListView(generics.ListAPIView):
    """FlagListView: ListAPIView
    for displaying a list of all flags"""
    permission_classes = (AllowAny,)

    queryset = Flag.objects.all()
    serializer_class = FlagSerializer


class SoftFlagListView(FlagListView):
    """SoftFlagListView: ListAPIView extends of FlagListView
    for displaying a list of all soft flags"""
    queryset = Flag.objects.filter(flag=False)


class HardFlagListView(FlagListView):
    """HardFlagListView: ListAPIView extends of FlagListView
    for displaying a list of all hard flags"""
    queryset = Flag.objects.filter(flag=True)


class MutedFlagListView(FlagListView):
    """MutedFlagListView: ListAPIView extends of FlagListView
    for displaying a list of all muted flags"""
    queryset = Flag.objects.filter(flag=None)
>>>>>>> rest247
