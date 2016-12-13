from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count
from serializers import (
    DetailEventCaseSerializer,
    CaseSerializer,
    RegionCaseSerializer
)
from Case.models import Case
from measurement.models import State


class DetailCaseRestView(generics.RetrieveAPIView):
    """DetailCaseRestView: RetrieveAPIView
    for displaying a specific case"""

    #   authentication_classes = (TokenAuthentication, BasicAuthentication)
    #   permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Case.objects.filter(draft=False)
    lookup_url_kwarg = 'case_id'
    serializer_class = CaseSerializer


class DetailEventCaseRestView(generics.RetrieveAPIView):
    """DetailEventCaseRestView: RetrieveAPIView
    for displaying a list of events of specific case"""
    #   authentication_classes = (TokenAuthentication, BasicAuthentication)
    #   permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Case.objects.filter(draft=False)
    lookup_url_kwarg = 'case_id'
    serializer_class = DetailEventCaseSerializer


class ListCaseView(generics.ListAPIView):
    """ListCaseView: ListAPIView
    for displaying a list of cases"""
    #   authentication_classes = (TokenAuthentication, BasicAuthentication)
    #   permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Case.objects.filter(draft=False)
    serializer_class = CaseSerializer


class ListRegionCaseView(generics.ListAPIView):
    """ListRegionCaseView: ListAPIView
    for displaying a list of regions with his cases"""
    permission_classes = (AllowAny,)
    queryset = State.objects.filter(
        country__name='Venezuela').annotate(
        num=Count('probes__flags__event__cases')).filter(
        num__gt=0)
    serializer_class = RegionCaseSerializer
