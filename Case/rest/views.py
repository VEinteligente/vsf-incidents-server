from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count
from serializers import (
    DetailEventCaseSerializer,
    CaseSerializer,
    RegionCaseSerializer,
    CaseFilter,
    DetailUpdateCaseSerializer
)
from Case.models import Case
from measurement.models import State

from django_filters.rest_framework import DjangoFilterBackend


class DetailCaseRestView(generics.RetrieveAPIView):
    """DetailCaseRestView: RetrieveAPIView
    for displaying a specific published case"""

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


class DetailUpdateCaseRestView(generics.RetrieveAPIView):
    #   authentication_classes = (TokenAuthentication, BasicAuthentication)
    #   permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Case.objects.filter(draft=False)
    lookup_url_kwarg = 'case_id'
    serializer_class = DetailUpdateCaseSerializer


class ListCaseView(generics.ListAPIView):
    """ListCaseView: ListAPIView
    for displaying a list of all published cases"""
    #   authentication_classes = (TokenAuthentication, BasicAuthentication)
    #   permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Case.objects.filter(draft=False)
    serializer_class = CaseSerializer


class ListRegionCaseView(generics.ListAPIView):
    """ListRegionCaseView: ListAPIView
    for displaying a list of regions with his published cases"""
    #   authentication_classes = (TokenAuthentication, BasicAuthentication)
    #   permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = State.objects.filter(
        country__name='Venezuela').annotate(
        num=Count('probes__flags__event__cases')).filter(
        num__gt=0)
    serializer_class = RegionCaseSerializer


class ListCaseFilterView(generics.ListAPIView):
    """ListCaseFilterView: ListAPIView
    for displaying a list of cases filtered by
    title, start date, end date, category and region"""
    #   authentication_classes = (TokenAuthentication, BasicAuthentication)
    #   permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Case.objects.filter(draft=False)
    serializer_class = CaseSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = CaseFilter

