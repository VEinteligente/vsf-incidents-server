from rest_framework import generics
from rest_framework.permissions import AllowAny

from measurement.models import Metric, Flag
from measurement.rest.serializers import FlagSerializer


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

    queryset = Metric.objects.all()
    serializer_class = MeasurementSerializer


class DNSMeasurementRestView(generics.ListAPIView):
    """DNSMeasurementRestView: MeasurementRestView
    for displaying a list of DNS measurements"""

    permission_classes = (AllowAny,)
    queryset = Metric.objects.filter(test_name='dns_consistency')
    serializer_class = DNSMeasurementSerializer


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

