import json

from rest_framework import serializers
from measurement.models import Metric, Flag, Probe, Plan
from measurement.front.views import DNSTestKey
from plugins.dns.serializer import DNSFlagSerializer


class MeasurementSerializer(serializers.ModelSerializer):
    """MeasurementSerializer: ModelSerializer
    for serialize a list of measurements"""

    flag = serializers.SerializerMethodField()

    class Meta:
        model = Metric
        exclude = ['id', ]

    def get_flag(self, obj):
        """
        Flag value of a measurement

        Args:
            obj: Metric object

        Returns:
            bool: False if soft flag, True if hard flag, 
            None if muted flag. Otherwise string "not"
        """
        flags = Flag.objects.filter(metric=obj.id).values('metric', 'flag')
        flag_value = None
        for flag in flags:
            if (str(flag['metric']) == str(obj.id)):
                flag_value = flag['flag']
        return flag_value


# class DNSMeasurementSerializer(MeasurementSerializer):
#     """DNSMeasurementSerializer: MeasurementSerializer
#     for serialize a list of DNS measurements"""

#     match = serializers.SerializerMethodField()
#     dns_isp = serializers.SerializerMethodField()
#     control_result = serializers.SerializerMethodField()
#     dns_result = serializers.SerializerMethodField()
#     dns_name = serializers.SerializerMethodField()

#     class Meta(MeasurementSerializer.Meta):
#         fields = ('flag', 'id', 'input', 'measurement_start_time', 'dns_isp',
#             'control_result', 'dns_name', 'dns_result', 'match')

#     def get_flag(self, obj):
#         """Flag value of a DNS measurement

#         Args:
#             obj: Metric object

#         Returns:
#             bool: False if soft flag, True if hard flag, 
#             None if muted flag. Otherwise string "not"
#         """
#         flags = Flag.objects.filter(
#             medicion=obj.id, type_med="DNS").values('medicion', 'flag')
#         flag_value = "not"
#         for flag in flags:
#             if (str(flag['medicion']) == str(obj.id)):
#                 flag_value = flag['flag']
#         return flag_value

#     def get_match(self, obj):
#         """If control result is equals to dns result
#         in DNS measurements

#         Args:
#             obj: Metric object

#         Returns:
#             bool: True if control result is equals to
#             dns result, otherwise False
#         """
#         return self.get_control_result == self.get_dns_result

#     def get_dns_isp(self, obj):
#         """Get DNS isp from measurement

#         Args:
#             obj: Metric object

#         Returns:
#             string: ISP provider
#         """
#         return "cantv"  # for now

#     def get_control_result(self, obj):
#         """Get control results

#         Args:
#             obj: Metric object

#         Returns:
#             list: A list of strings with each of the control
#             results of a DNS measurement
#         """

#         test_key = DNSTestKey(json.dumps(obj.test_keys))
#         queries = test_key.get_queries()
#         control_resolver = ""
#         if not queries[0]['failure'] and queries[0]['answers']:

#             # Get answers #
#             answers = queries[0]['answers']

#             # Get control resolver from answer_type A #
#             for a in answers:
#                 if a['answer_type'] == 'A':
#                     control_resolver = a['ipv4']
#         return control_resolver

#     def get_dns_name(self, obj):
#         """Get DNS name

#         Args:
#             obj: Metric object

#         Returns:
#             string: The resolver_hostname of the measurement
#         """
#         test_key = DNSTestKey(json.dumps(obj.test_keys))
#         queries = test_key.get_queries()
#         dns_name = ""
#         if not queries[0]['failure'] and queries[0]['answers']:
#             dns_name = queries[0]['resolver_hostname']
#         return dns_name

#     def get_dns_result(self, obj):
#         """Get DNS results

#         Args:
#             obj: Metric object

#         Returns:
#             list: A list of strings with each of the DNS
#             results of a DNS measurement
#         """
#         test_key = DNSTestKey(json.dumps(obj.test_keys))
#         queries = test_key.get_queries()
#         dns_result = ""
#         for query in queries:
#             if query['failure']:
#                 dns_result = query['failure']
#             else:
#                 answers = query['answers']
#                 for a in answers:
#                     if a['answer_type'] == 'A':
#                         dns_result = a['ipv4']
#         return dns_result


class PlanSerializer(serializers.ModelSerializer):
    """PlanSerializer: ModelSerializer
    for serialize a plan object"""
    class Meta:
        model = Plan


class PlanFlagSerializer(PlanSerializer):
    """PlanFlagSerializer: ModelSerializer extends of PlanSerializer
    for serialize a plan object excluding id field"""
    class Meta(PlanSerializer.Meta):
        exclude = ('id',)


class ProbeSerializer(serializers.ModelSerializer):
    """ProbeSerializer: ModelSerializer
    for serialize a probe object"""
    class Meta:
        model = Probe


class ProbeFlagSerializer(ProbeSerializer):
    """ProbeFlagSerializer: ModelSerializer extends of ProbeSerializer
    for serialize a probe object excluding id field and adding
    new field definition for region, country and plan fields"""
    region = serializers.StringRelatedField()
    country = serializers.StringRelatedField()
    plan = PlanFlagSerializer(read_only=True)

    class Meta(ProbeSerializer.Meta):
        exclude = ('id',)


class FlagSerializer(serializers.ModelSerializer):
    """FlagSerializer: ModelSerializer
    for serialize a flag object"""
    metric = serializers.SerializerMethodField()

    class Meta:
        model = Flag
        exclude = ('id', 'suggested_events')

    def get_metric(self, obj):
        return obj.metric.measurement


