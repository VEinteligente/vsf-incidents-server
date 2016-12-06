from rest_framework import serializers
from event.models import Event, Url, Site


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


class SiteSerializer(serializers.ModelSerializer):
    domains = serializers.SerializerMethodField()

    @staticmethod
    def get_domains(obj):
        dm = Url.objects.filter(site=obj)
        return UrlSerializer(dm, many=True).data

    class Meta:
        model = Site
