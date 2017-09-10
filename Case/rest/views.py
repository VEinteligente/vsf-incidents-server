from rest_framework import generics
from rest_framework.authentication import BasicAuthentication
from vsf.vsf_authentication import VSFTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from serializers import (
    DetailEventCaseSerializer,
    CaseSerializer,
    CaseFilter,
    DetailUpdateCaseSerializer,
    CategoryCaseSerializer,
    ISPCaseSerializer,
    CategorySerializer,
    RegionSerializer,
    ISPSerializer,
    GanttChartSerializer,
    EventsByMonthSerializer,
    ListCountEventsByRegionByCaseSerializer,
    CaseFlagsSerializer
)
from event.models import Event
from Case.models import Case, Category
from measurement.models import State, Flag, ISP

from plugins.views import DatatablesView

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


class DetailFlagCaseRestView(generics.RetrieveAPIView):
    """DetailFlagCaseRestView: RetrieveAPIView
    for displaying a list of updates of specific published case"""
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Case.objects.filter(draft=False)
    lookup_url_kwarg = 'case_id'
    serializer_class = CaseFlagsSerializer


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


# class ListRegionCaseView(generics.ListAPIView):
#     """
#     ListRegionCaseView: ListAPIView
#     for displaying a list of regions with his published cases
#     """
#     authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
#     permission_classes = (IsAuthenticated,)
#     queryset = State.objects.filter(
#         country__name='Venezuela').annotate(
#         num=Count('probes__flags__event__cases')).filter(
#         num__gt=0)
#     serializer_class = RegionCaseSerializer


class ListCountEventsByRegionByCase(generics.RetrieveAPIView):
    """
    ListCountEventsByRegionByCase: RetrieveAPIView
    for displaying a list of regions with number of events
    gived one case
    """
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Case.objects.filter(draft=False)
    serializer_class = ListCountEventsByRegionByCaseSerializer
    lookup_url_kwarg = 'case_id'
    lookup_field = 'pk'


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


class ListISPView(generics.ListAPIView):
    """ListISPView: ListAPIView
    for displaying a list of ISP """
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    # queryset = Event.objects.filter(
    #     draft=False).values('isp').order_by('isp').distinct()
    queryset = ISP.objects.all()
    serializer_class = ISPSerializer


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


class GanttChart(generics.RetrieveAPIView):
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = 'case_id'
    queryset = Case.objects.filter(draft=False)
    serializer_class = GanttChartSerializer


class EventsByMonth(GanttChart):
    serializer_class = EventsByMonthSerializer


class FrontCaseAjaxView(DatatablesView):
    """
    FrontCaseAjaxView: DatatablesView for fill Case metrics table.
    Field checkbox is required to do functions over the table and must be
    the id to identify which metric is selected.
    Field measurement_id is required if measurement field is present
    Field checkbox, flag, test_keys, measurement, report_id are customized by
    table.html
    """
    authentication_classes = (VSFTokenAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    pk_url_kwarg = 'case_id'
    fields = {
        'checkbox': 'uuid',
        'Flag': 'flag',
        'manual_flag': 'manual_flag',
        'flag_id': 'uuid',
        'probe_isp': 'metric__probe__isp__name',
        'input': 'metric__input',
        'report_id': 'metric__report_id',
        'test_name': 'metric__test_name',
        'test_start_time': 'metric__test_start_time',
        'measurement_start_time': 'metric__measurement_start_time'
    }
    queryset = Flag.objects.all()

    def get_queryset(self):
        """
        Apply Datatables sort and search criterion to QuerySet
        :return: queryset
        """
        case_pk = self.kwargs.get(self.pk_url_kwarg)
        case = Case.objects.get(id=case_pk)
        events = Event.objects.filter(cases=case).values_list('id')
        self.queryset = self.queryset.filter(event__id__in=events)
        return super(FrontCaseAjaxView, self).get_queryset()
