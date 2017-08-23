import django_filters
from rest_framework import serializers
from django.db.models import Q, Count
from plugins.ndt.models import NDT, DailyTest


class CharInFilter(django_filters.BaseInFilter,
                   django_filters.CharFilter):
    """CharInFilter: BaseInFilter for a comma separated
    fields for a CharFilter"""
    pass


class NDTSerializer(serializers.ModelSerializer):

    class Meta:
        model = NDT


class DailyTestSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyTest


class NDTFilter(django_filters.FilterSet):

    start_date = django_filters.DateFilter(name='date', lookup_expr='gte')
    end_date = django_filters.DateFilter(name='date', lookup_expr='lte')
    regions = CharInFilter(
        name='flag__metric__probe__region__name',
        distinct=True
    )
    isp = CharInFilter(
        name='isp__name',
        distinct=True
    )
    plan = CharInFilter(
        name='flag__metric__probe__plan__name',
        distinct=True
    )

    class Meta:
        model = NDT
        fields = ('start_date', 'end_date', 'regions', 'isp', 'plan')


class DailyTestFilter(django_filters.FilterSet):

    start_date = django_filters.DateFilter(name='date', lookup_expr='gte')
    end_date = django_filters.DateFilter(name='date', lookup_expr='lte')
    regions = CharInFilter(
        name='flag__metric__probe__region__name',
        distinct=True
    )
    isp = CharInFilter(
        name='isp__name',
        distinct=True
    )
    plan = CharInFilter(
        name='flag__metric__probe__plan__name',
        distinct=True
    )

    class Meta:
        model = DailyTest
        fields = ('start_date', 'end_date', 'regions', 'isp', 'plan')
