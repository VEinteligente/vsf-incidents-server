from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import generics

from measurement.rest import serializers
from measurement.models import Metric, Flag
from measurement.rest.serializers import FlagSerializer


class MeasurementRestView(APIView):
    """MeasurementRestView: APIView
    for displaying a list of measurements"""
    permission_classes = (AllowAny,)

    def get(self, request):
        """List measurements"""
        serializer = serializers.MeasurementSerializer(
            Metric.objects.all().first())
        return Response(serializer.data)


class DNSMeasurementRestView(MeasurementRestView):
    """DNSMeasurementRestView: MeasurementRestView
    for displaying a list of DNS measurements"""

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
