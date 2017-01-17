from rest_framework import generics
from rest_framework.authentication import BasicAuthentication
from vsf.vsf_authentication import VSFTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from serializers import (
    DetailEventCaseSerializer,
    CaseSerializer,
    RegionCaseSerializer,
    CaseFilter,
    DetailUpdateCaseSerializer,
    CategoryCaseSerializer,
    ISPCaseSerializer,
    CategorySerializer,
    RegionSerializer
)
from event.models import Event
from Case.models import Case, Category
from measurement.models import State

from django_filters.rest_framework import DjangoFilterBackend


class DetailCaseRestView(generics.RetrieveAPIView):
    """DetailCaseRestView: RetrieveAPIView
    for displaying a specific published case"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Case.objects.filter(draft=False)
    lookup_url_kwarg = 'case_id'
    serializer_class = CaseSerializer


class DetailEventCaseRestView(generics.RetrieveAPIView):
    """DetailEventCaseRestView: RetrieveAPIView
    for displaying a list of events of specific published case"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Case.objects.filter(draft=False)
    lookup_url_kwarg = 'case_id'
    serializer_class = DetailEventCaseSerializer


class DetailUpdateCaseRestView(generics.RetrieveAPIView):
    """DetailUpdateCaseRestView: RetrieveAPIView
    for displaying a list of updates of specific published case"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Case.objects.filter(draft=False)
    lookup_url_kwarg = 'case_id'
    serializer_class = DetailUpdateCaseSerializer


class ListCaseView(generics.ListAPIView):
    """ListCaseView: ListAPIView
    for displaying a list of all published cases"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Case.objects.filter(draft=False)
    serializer_class = CaseSerializer


class ListRegionView(generics.ListAPIView):
    """ListRegionView: ListAPIView
    for displaying a list of regions """
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = State.objects.filter(
        country__name='Venezuela')
    serializer_class = RegionSerializer


class ListRegionCaseView(generics.ListAPIView):
    """ListRegionCaseView: ListAPIView
    for displaying a list of regions with his published cases"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = State.objects.filter(
        country__name='Venezuela').annotate(
        num=Count('probes__flags__event__cases')).filter(
        num__gt=0)
    serializer_class = RegionCaseSerializer


class ListCategoryView(generics.ListAPIView):
    """ListCategoryView: ListAPIView
    for displaying a list of categories"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ListCategoryCaseView(generics.ListAPIView):
    """ListCategoryCaseView: ListAPIView
    for displaying a list of categories with his published cases"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategoryCaseSerializer


class ListISPCaseView(generics.ListAPIView):
    """ListISPCaseView: ListAPIView
    for displaying a list of isp with his published cases"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Event.objects.filter(
        draft=False).values('isp').order_by('isp').distinct()
    serializer_class = ISPCaseSerializer


class ListCaseFilterView(generics.ListAPIView):
    """ListCaseFilterView: ListAPIView
    for displaying a list of cases filtered by
    title, start date, end date, domain, site,
    isp, category and region"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Case.objects.filter(draft=False)
    serializer_class = CaseSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = CaseFilter
