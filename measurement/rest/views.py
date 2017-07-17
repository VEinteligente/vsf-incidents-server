from rest_framework import generics
from rest_framework.authentication import BasicAuthentication
from vsf.vsf_authentication import VSFTokenAuthentication
from rest_framework.permissions import IsAuthenticated

from measurement.models import Metric, Flag
from measurement.rest.serializers import FlagSerializer

from serializers import (
    MeasurementSerializer,
    # DNSMeasurementSerializer
)


class MeasurementRestView(generics.ListAPIView):
    """MeasurementRestView: APIView
    for displaying a list of measurements"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = Metric.objects.all()
    serializer_class = MeasurementSerializer


# class DNSMeasurementRestView(generics.ListAPIView):
#     """DNSMeasurementRestView: MeasurementRestView
#     for displaying a list of DNS measurements"""
#     authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
#     permission_classes = (IsAuthenticated,)

#     queryset = Metric.objects.filter(test_name='dns_consistency')
#     serializer_class = DNSMeasurementSerializer


class FlagListView(generics.ListAPIView):
    """FlagListView: ListAPIView
    for displaying a list of all flags"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = Flag.objects.all()
    serializer_class = FlagSerializer


class SoftFlagListView(FlagListView):
    """SoftFlagListView: ListAPIView extends of FlagListView
    for displaying a list of all soft flags"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = Flag.objects.filter(flag=Flag.SOFT)


class HardFlagListView(FlagListView):
    """HardFlagListView: ListAPIView extends of FlagListView
    for displaying a list of all hard flags"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = Flag.objects.filter(flag=Flag.HARD)


class MutedFlagListView(FlagListView):
    """MutedFlagListView: ListAPIView extends of FlagListView
    for displaying a list of all muted flags"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = Flag.objects.filter(flag=Flag.MUTED)


# No tiene url
class NDTMetrics(generics.ListAPIView):
    """

    """
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = Flag.objects.filter(flag=Flag.NONE, plugin_name='ndt')


class DetailFlagRestView(generics.RetrieveAPIView):
    """DetailFlagRestView: RetrieveAPIView
    for displaying a specific flag"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Flag.objects.all()
    lookup_url_kwarg = 'flag_id'
    lookup_field = 'uuid'
    serializer_class = FlagSerializer
