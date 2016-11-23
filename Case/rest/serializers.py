import json

from rest_framework import serializers
from Case.models import Case

class CaseSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Case