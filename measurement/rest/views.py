from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from measurement.rest import serializers
from measurement.models import Metric


class MeasurementRestView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
    	serializer = serializers.MeasurementSerializer(Metric.objects.all().first())
    	return Response(serializer.data)


class DNSMeasurementRestView(MeasurementRestView):

    def get(self, request):
    	serializer = serializers.DNSMeasurementSerializer(
    		Metric.objects.filter(test_name='dns_consistency').first())
    	return Response(serializer.data)