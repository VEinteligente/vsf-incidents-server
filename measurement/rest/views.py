from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from measurement.rest import serializers
from measurement.models import Metric


class MeasurementRestView(APIView):
    """MeasurementRestView: APIView
    for displaying a list of measurements"""
    permission_classes = (AllowAny,)

    def get(self, request):
        """List measurements"""
        serializer = serializers.MeasurementSerializer(Metric.objects.all().first())
        return Response(serializer.data)


class DNSMeasurementRestView(MeasurementRestView):
    """DNSMeasurementRestView: MeasurementRestView
    for displaying a list of DNS measurements"""

    def get(self, request):
        """List DNS measurements"""
        serializer = serializers.DNSMeasurementSerializer(
            Metric.objects.filter(test_name='dns_consistency').first())
        return Response(serializer.data)
