from rest_framework import serializers
from .models import DNS


class DNSSerializer(serializers.ModelSerializer):
    """DNSSerializer: ModelSerializer
    for serialize a DNS object"""
    class Meta:
        model = DNS


class DNSFlagSerializer(DNSSerializer):
    class Meta(DNSSerializer.Meta):
        exclude = ('id', 'metric', 'flag')

