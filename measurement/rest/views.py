from rest_framework import generics
from rest_framework.permissions import AllowAny

from measurement.models import Metric

from serializers import (
    MeasurementSerializer,
    DNSMeasurementSerializer
)


class MeasurementRestView(generics.ListAPIView):
    """MeasurementRestView: APIView
    for displaying a list of measurements"""
    # authentication_classes = (TokenAuthentication, BasicAuthentication)
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Metric.objects.all()
    serializer_class = MeasurementSerializer


class DNSMeasurementRestView(generics.ListAPIView):
    """DNSMeasurementRestView: MeasurementRestView
    for displaying a list of DNS measurements"""
    permission_classes = (AllowAny,)
    queryset = Metric.objects.filter(test_name='dns_consistency')
    serializer_class = DNSMeasurementSerializer
