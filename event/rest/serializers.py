from django.db.models import Q, Count
from rest_framework import serializers
from event.models import Event, Url, Site

import django_filters


class EventSerializer(serializers.ModelSerializer):
    """EventSerializer: ModelSerializer
    for serialize a list of events"""

    target = serializers.StringRelatedField()

    class Meta:
        model = Event
        fields = ('isp', 'start_date', 'end_date', 'target', 'identification', 'type')


class UrlSerializer(serializers.ModelSerializer):
    site = serializers.StringRelatedField()

    class Meta:
        model = Url


class UrlFlagSerializer(UrlSerializer):
    class Meta(UrlSerializer.Meta):
        exclude = ('id',)


class SiteSerializer(serializers.ModelSerializer):
    domains = serializers.SerializerMethodField()

    @staticmethod
    def get_domains(obj):

        events = Event.objects.filter(
            Q(type='bloqueo por DPI') |
            Q(type='bloqueo por DNS') |
            Q(type='bloqueo por IP')
        )
        url_list = events.values('target')

        dm = Url.objects.filter(site=obj, id__in=url_list)
        return UrlSerializer(dm, many=True).data

    class Meta:
        model = Site


class EventGroupSerializer(serializers.ModelSerializer):

    events = serializers.SerializerMethodField()
    number_events = serializers.SerializerMethodField()

    @staticmethod
    def get_events(obj):
        """Events of a specific isp and type

        Args:
            obj: Event

        Returns:
            List of events of specific isp and type
        """
        events = Event.objects.filter(isp=obj.isp,
                                      type=obj.type)

        return EventSerializer(events, many=True).data

    @staticmethod
    def get_number_events(obj):
        """Number of events of a specific isp and type

        Args:
            obj: Event

        Returns:
            Integer with que number of events
        """
        events = Event.objects.filter(isp=obj.isp,
                                      type=obj.type)
        events = set(events)
        return len(events)

    class Meta:
        model = Event
        fields = ('isp', 'type', 'events', 'number_events')


# Django Filter EventGroupFilter

class EventGroupFilter(django_filters.FilterSet):

    start_date = django_filters.DateFilter(lookup_expr='gte')
    end_date = django_filters.DateFilter(lookup_expr='lte')

    class Meta:
        model = Event
        fields = ('start_date', 'end_date')
