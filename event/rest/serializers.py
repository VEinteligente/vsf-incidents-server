from rest_framework import serializers
from event.models import Event


class EventSerializer(serializers.ModelSerializer):
    """EventSerializer: ModelSerializer
    for serialize a list of events"""

    class Meta:
        model = Event
