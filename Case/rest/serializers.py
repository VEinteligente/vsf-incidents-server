import json

from rest_framework import serializers
from Case.models import Case
from measurement.models import State
from event.rest.serializers import EventSerializer, UrlSerializer
from event.models import Url

import django_filters


class CaseSerializer(serializers.ModelSerializer):
    """CaseSerializer: ModelSerializer
    for serialize a Case object with an additional attribute isp"""
    events = serializers.StringRelatedField(many=True)
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


class DetailEventCaseSerializer(serializers.ModelSerializer):

    events = EventSerializer(many=True, read_only=True)

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
            events__flags__probe__region=obj)
        cases = set(cases)
        return len(cases)


# Django Filter

class CaseFilter(django_filters.FilterSet):
    region = django_filters.CharFilter(
        name='events__flags__region',
        distinct=True
    )
    start_date = django_filters.DateFilter()
    end_date = django_filters.DateFilter()
    domain = django_filters.CharFilter(
        name='events__target__url',
        distinct=True
    )
    site = django_filters.CharFilter(
        name='events__target__site__name',
        distinct=True
    )

    class Meta:
        model = Case
        fields = ('title', 'category', 'start_date', 'end_date', 'region', 'domain', 'site')
