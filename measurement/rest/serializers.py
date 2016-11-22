import json

from rest_framework import serializers
from measurement.models import Metric, Flag
from measurement.front.views import DNSTestKey

class MeasurementSerializer(serializers.ModelSerializer):
	flag = serializers.SerializerMethodField()
	class Meta:
		model = Metric

	def get_flag(self, obj):
		flags = Flag.objects.filter(medicion=obj.id).values('medicion', 'flag')
		flag_value = "not"
		for flag in flags:
		    if (str(flag['medicion']) == str(obj.id)):
		        flag_value = flag['flag']
		return flag_value

class DNSMeasurementSerializer(MeasurementSerializer):
	match = serializers.SerializerMethodField()
	dns_isp = serializers.SerializerMethodField()
	control_result = serializers.SerializerMethodField()
	dns_result = serializers.SerializerMethodField()
	dns_name = serializers.SerializerMethodField()

	class Meta(MeasurementSerializer.Meta):
		fields = ('flag', 'id', 'input', 'measurement_start_time', 'dns_isp',
			'control_result', 'dns_name', 'dns_result', 'match')

	def get_flag(self, obj):
		flags = Flag.objects.filter(
			medicion=obj.id, type_med="DNS").values('medicion', 'flag')
		flag_value = "not"
		for flag in flags:
		    if (str(flag['medicion']) == str(obj.id)):
		        flag_value = flag['flag']
		return flag_value
	
	def get_match(self, obj):
		return self.get_control_result == self.get_dns_result

	def get_dns_isp(self, obj):
		return "cantv" # for now

	def get_control_result(self,obj):
		test_key = DNSTestKey(json.dumps(obj.test_keys))
		queries = test_key.get_queries()
		control_resolver = ""
		if not queries[0]['failure'] and queries[0]['answers']:

		    # Get answers #
			answers = queries[0]['answers']

		    # Get control resolver from answer_type A #
			for a in answers:
				if a['answer_type'] == 'A':
					control_resolver = a['ipv4']
		return control_resolver

	def get_dns_name(self, obj):
		test_key = DNSTestKey(json.dumps(obj.test_keys))
		queries = test_key.get_queries()
		dns_name = ""
		if not queries[0]['failure'] and queries[0]['answers']:
			dns_name = queries[0]['resolver_hostname']
		return dns_name

	def get_dns_result(self, obj):
		test_key = DNSTestKey(json.dumps(obj.test_keys))
		queries = test_key.get_queries()
		dns_result = ""
		for query in queries:
			if query['failure']:
				dns_result = query['failure']
			else:
				answers = query['answers']
				for a in answers:
					if a['answer_type'] == 'A':
						dns_result = a['ipv4']
		return dns_result          