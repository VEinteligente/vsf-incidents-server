from measurement.models import Metric, MetricFlag

# Create your flag tests here.


def first_test():
    metric = Metric.objects.all()
    # do some stuff with metrics


def second_test():
    flags_in_measurements_data_base = MetricFlag.objects.all()
    # do some other stuff with this flags
