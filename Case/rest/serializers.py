import json
import datetime
import calendar

from django.db.models import Q
from rest_framework import serializers
from Case.models import Case, Update, Category
from measurement.models import State, Probe
from event.rest.serializers import EventSerializer, UrlSerializer
from event.models import Url, Site

import django_filters


class CaseSerializer(serializers.ModelSerializer):
    """CaseSerializer: ModelSerializer
    for serialize a Case object with an additional fields events (just ID's),
    updates (just title) and isp"""
    events = serializers.StringRelatedField(many=True)
    updates = serializers.StringRelatedField(many=True)
    isp = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    domains = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Case

    def get_isp(self, obj):
        """ISP List value of a case

        Args:
            obj: Case object

        Returns:
            isp: list of isp of all events in the case (obj)
        """
        isp = []
        for event in obj.events.all():
            isp.append(event.isp)
        return isp

    def get_region(self, obj):
        """Region List value of a case

        Args:
            obj: Case object

        Returns:
            region: list of regions of all events in the case (obj)
        """
        region = []
        for event in obj.events.all():
            for flag in event.flags.all():
                region.append(flag.region)
        return list(set(region))

    def get_domains(self, obj):
        url_list = obj.events.all().values('target')
        dm = Url.objects.filter(id__in=url_list)
        return UrlSerializer(dm, many=True).data

    def get_category(self, obj):
        """Name of the category

        Args:
            obj: case Objects

        Returns:
            value of dict {'name': name, 'display_name': display_name}
        """
        category = Category.objects.get(id=obj.category.id)
        name = category.name
        display_name = category.display_name

        return {'name': name, 'display_name': display_name}


class GanttChartSerializer(CaseSerializer):

    events = serializers.SerializerMethodField()

    def get_events(self, obj):
        events = obj.events.order_by(
            'isp',
            'target__site__name',
            'start_date'
        )
        return EventSerializer(events, many=True).data

    class Meta(CaseSerializer.Meta):
        fields = ('events',)


class EventsByMonthSerializer(CaseSerializer):

    dates = serializers.SerializerMethodField()

    def in_month_year(self, month, year):
        d_fmt = "{0:>02}.{1:>02}.{2}"
        date_from = datetime.datetime.strptime(
            d_fmt.format(1, month, year), '%d.%m.%Y').date()
        last_day_of_month = calendar.monthrange(year, month)[1]
        date_to = datetime.datetime.strptime(
            d_fmt.format(last_day_of_month, month, year), '%d.%m.%Y').date()
        return self.events.filter(
            Q(start_date__gte=date_from, start_date__lte=date_to)
            |
            Q(start_date__lt=date_from, start_date__gte=date_from)
        )

    def get_dates(self, obj):
        start_date = obj.start_date
        end_date = obj.end_date
        self.events = obj.events.all()
        result = {}
        if not end_date:
            end_date = datetime.datetime.now()
        years = int(end_date.year) - int(start_date.year)
        month = (years * 12) - start_date.month + end_date.month + 1
        for i in range(0, month):
            month = start_date.month - 1 + i
            year = int(start_date.year + month / 12)
            month = month % 12 + 1
            day = min(start_date.day, calendar.monthrange(year, month)[1])
            result[calendar.month_name[month]+' - '+str(year)] = self.in_month_year(month=month, year=year).count()

        return result

    class Meta(CaseSerializer.Meta):
        fields = ('dates',)


class UpdateSerializer(serializers.ModelSerializer):
    """UpdateSerializer: ModelSerializer
    for serialize a Update object. Excluding fields case and created by"""
    class Meta:
        model = Update
        exclude = ('case', 'created_by')


class DetailUpdateCaseSerializer(serializers.ModelSerializer):
    """DetailUpdateCaseSerializer: ModelSerializer
    for serialize a case with his updates (including details of the updates)"""
    updates = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Case

    def get_updates(self, obj):
        queryset = obj.updates.all().order_by('-date')
        return UpdateSerializer(queryset, many=True).data

    def get_category(self, obj):
        """Name of the category

        Args:
            obj: case Objects

        Returns:
            value of dict {'name': name, 'display_name': display_name}
        """
        category = Category.objects.get(id=obj.category.id)
        name = category.name
        display_name = category.display_name

        return {'name': name, 'display_name': display_name}


class DetailEventCaseSerializer(serializers.ModelSerializer):
    """DetailEventCaseSerializer: ModelSerializer
    for serialize a case with his events (including details of the events)"""
    events = serializers.SerializerMethodField()
    updates = serializers.StringRelatedField(many=True)
    category = serializers.SerializerMethodField()

    class Meta:
        model = Case

    def get_events(self, obj):
        queryset = obj.events.all().order_by('-start_date')
        return EventSerializer(queryset, many=True).data

    def get_category(self, obj):
        """Name of the category

        Args:
            obj: case Objects

        Returns:
            value of dict {'name': name, 'display_name': display_name}
        """
        category = Category.objects.get(id=obj.category.id)
        name = category.name
        display_name = category.display_name

        return {'name': name, 'display_name': display_name}


class RegionSerializer(serializers.ModelSerializer):
    """RegionSerializer: ModelSerializer
    for serialize a State object"""
    class Meta:
        model = State


class RegionCaseSerializer(RegionSerializer):
    """RegionSerializer: ModelSerializer extention of RegionSerializer
    with additional attributes Cases (all cases in that region) and
    number_cases (count of all cases in that region)"""
    cases = serializers.SerializerMethodField()
    number_cases = serializers.SerializerMethodField()

    class Meta(RegionSerializer.Meta):
        fields = ('cases', 'name', 'number_cases')

    def get_cases(self, obj):
        """List of all cases in a specific region

        Args:
            obj: State object

        Returns:
            List of cases using CasesSerializer
        """
        cases = Case.objects.filter(
            draft=False,
            events__flags__probe__region=obj)
        cases = set(cases)
        return CaseSerializer(cases, many=True, read_only=True).data

    def get_number_cases(self, obj):
        """Number of cases in a specific region

        Args:
            obj: State object

        Returns:
            Integer with que number of cases
        """
        cases = Case.objects.filter(
            draft=False,
            events__flags__probe__region=obj)
        cases = set(cases)
        return len(cases)


class CategorySerializer(serializers.Serializer):
    """CategorySerializer: Serializer
    for serialize the categories of the cases"""
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        """Name of the category

        Args:
            obj: dict {'category': 'value'}

        Returns:
            value of dict {'category': {
                'name': obj.name, 'display_name': obj.display_name}
            }
        """
        return {'name': obj.name, 'display_name': obj.display_name}


class CategoryCaseSerializer(CategorySerializer):
    """CategoryCaseSerializer: Serializer extention of CategorySerializer
    for serialize the categories of the cases, with all cases of that 
    category and how many there are"""
    cases = serializers.SerializerMethodField()
    number_cases = serializers.SerializerMethodField()

    def get_cases(self, obj):
        """List of all cases in a specific category

        Args:
            obj: dict {'category': 'value'}

        Returns:
            List of cases using CasesSerializer
        """
        cases = Case.objects.filter(
            draft=False,
            category=obj)
        return CaseSerializer(cases, many=True, read_only=True).data

    def get_number_cases(self, obj):
        """Number of cases in a specific category

        Args:
            obj: dict {'category': 'value'}

        Returns:
            Integer with que number of cases
        """
        cases = Case.objects.filter(
            draft=False,
            category=obj)
        return len(cases)


class ISPSerializer(serializers.Serializer):
    """ISPCaseSerializer: Serializer
    for serialize the ISP of the cases"""
    isp = serializers.SerializerMethodField()

    def get_isp(self, obj):
        """ Name of the isp

        Args:
            obj: dict {'isp': 'value'}

        Returns:
           value of dict {'isp': 'value'}
        """
        return obj['isp']


class ISPCaseSerializer(ISPSerializer):
    """ISPCaseSerializer: Serializer extends of ISPSerializer
    for serialize the ISP of the cases, with all cases with that 
    ISP and how many there are"""
    cases = serializers.SerializerMethodField()
    number_cases = serializers.SerializerMethodField()

    def get_cases(self, obj):
        """List of all cases in a specific isp

        Args:
            obj: dict {'isp': 'value'}

        Returns:
            List of cases using CasesSerializer
        """
        cases = Case.objects.filter(
            draft=False,
            events__isp=obj['isp'])
        cases = set(cases)
        return DetailEventCaseSerializer(cases, many=True, read_only=True).data

    def get_number_cases(self, obj):
        """Number of cases in a specific isp

        Args:
            obj: dict {'isp': 'value'}

        Returns:
            Integer with que number of cases
        """
        cases = Case.objects.filter(
            draft=False,
            events__isp=obj['isp'])
        cases = set(cases)
        return len(cases)


class ListCountEventsByRegionByCaseSerializer(CaseSerializer):

    regions = serializers.SerializerMethodField()

    @staticmethod
    def get_regions(obj):
        events = obj.events.all()
        result = {}
        for event in events:
            flags = event.flags.all()
            for flag in flags:
                probe = flag.probe
                if probe.region.name not in result:
                    result[probe.region.name] = 1
                else:
                    result[probe.region.name] += 1
        return result

    class Meta(CaseSerializer):
        model = Case
        fields = ('regions',)


# Django Filter CaseFilter

class CharInFilter(django_filters.BaseInFilter,
                   django_filters.CharFilter):
    """CharInFilter: BaseInFilter for a comma separated
    fields for a CharFilter"""
    pass


class CaseFilter(django_filters.FilterSet):
    """CaseFilter: FilterSet for filter a Case by
    region, start_date, end_date, domain, site, 
    isp and category"""
    region = CharInFilter(
        name='events__flags__region',
        distinct=True
    )
    start_date = django_filters.DateFilter(lookup_expr='gte')
    end_date = django_filters.DateFilter(lookup_expr='lte')
    domain = CharInFilter(
        name='events__target__url',
        distinct=True
    )
    site = CharInFilter(
        name='events__target__site__name',
        distinct=True
    )
    isp = CharInFilter(
        name='events__isp',
        distinct=True
    )
    category = CharInFilter(
        name='category__name',
        distinct=True
    )

    class Meta:
        model = Case
        fields = ('title', 'category', 'start_date', 'end_date', 'region', 'domain', 'site', 'isp')
