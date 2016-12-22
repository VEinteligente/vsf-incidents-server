import json

from rest_framework import serializers
from Case.models import Case, Update
from measurement.models import State
from event.rest.serializers import EventSerializer, UrlSerializer
from event.models import Url

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


class UpdateSerializer(serializers.ModelSerializer):
    """UpdateSerializer: ModelSerializer
    for serialize a Update object. Excluding fields case and created by"""
    class Meta:
        model = Update
        exclude = ('case', 'created_by')


class DetailUpdateCaseSerializer(serializers.ModelSerializer):
    """DetailUpdateCaseSerializer: ModelSerializer
    for serialize a case with his updates (including details of the updates)"""
    updates = UpdateSerializer(many=True, read_only=True)

    class Meta:
        model = Case


class DetailEventCaseSerializer(serializers.ModelSerializer):
    """DetailEventCaseSerializer: ModelSerializer
    for serialize a case with his events (including details of the events)"""
    events = EventSerializer(many=True, read_only=True)
    updates = serializers.StringRelatedField(many=True)

    class Meta:
        model = Case


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
            value of dict {'category': 'value'}
        """
        return obj


class CategoryCaseSerializer(CategorySerializer):
    """CategoryCaseSerializer: Serializer extention of CategorySerializer
    for serialize the categories of the cases, with all cases of that 
    category and how many there are"""
    cases = serializers.SerializerMethodField()
    number_cases = serializers.SerializerMethodField()

    def get_category(self, obj):
        """Name of the category

        Args:
            obj: dict {'category': 'value'}

        Returns:
            value of dict {'category': 'value'}
        """

        return obj['category']

    def get_cases(self, obj):
        """List of all cases in a specific category

        Args:
            obj: dict {'category': 'value'}

        Returns:
            List of cases using CasesSerializer
        """
        cases = Case.objects.filter(
            draft=False,
            category=obj['category'])
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
            category=obj['category'])
        return len(cases)


class ISPCaseSerializer(serializers.Serializer):
    """ISPCaseSerializer: Serializer
    for serialize the ISP of the cases, with all cases with that 
    ISP and how many there are"""
    isp = serializers.SerializerMethodField()
    cases = serializers.SerializerMethodField()
    number_cases = serializers.SerializerMethodField()

    def get_isp(self, obj):
        """ Name of the isp

        Args:
            obj: dict {'isp': 'value'}

        Returns:
           value of dict {'isp': 'value'}
        """
        return obj['isp']

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

    class Meta:
        model = Case
        fields = ('title', 'category', 'start_date', 'end_date', 'region', 'domain', 'site', 'isp')
