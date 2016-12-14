import json

from rest_framework import serializers
from Case.models import Case, Update
from measurement.models import State
from event.rest.serializers import EventSerializer

import django_filters


class CaseSerializer(serializers.ModelSerializer):
    """CaseSerializer: ModelSerializer
    for serialize a Case object with an additional fields events (just ID's),
    updates (just title) and isp"""
    events = serializers.StringRelatedField(many=True)
    updates = serializers.StringRelatedField(many=True)
    isp = serializers.SerializerMethodField()

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


class CategoryCaseSerializer(serializers.Serializer):
    category = serializers.SerializerMethodField()
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

# Django Filter


class CaseFilter(django_filters.FilterSet):
    region = django_filters.CharFilter(
        name='events__flags__region',
        distinct=True
    )
    start_date = django_filters.DateFilter()
    end_date = django_filters.DateFilter()

    class Meta:
        model = Case
        fields = ('title', 'category', 'start_date', 'end_date', 'region')
