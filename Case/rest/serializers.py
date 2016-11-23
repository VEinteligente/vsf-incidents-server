import json

from rest_framework import serializers
from Case.models import Case
from event.rest.serializers import EventSerializer


class CaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Case


class DetailEventCaseSerializer(serializers.ModelSerializer):

    events = EventSerializer(many=True, read_only=True)

    class Meta:
        model = Case
