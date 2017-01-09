from measurement.models import Flag
from event.models import Url


def change_to_manual_flag(metric, metric_ip, metric_isp, flag_type, type_med):

    flags = metric.flags.all()

    if not flags:
        url, created = Url.objects\
                          .get_or_create(url=metric.input)

        flag = Flag.objects.create(ip=metric_ip,
                                   flag=flag_type,
                                   manual_flag=True,
                                   date=metric.measurement_start_time,
                                   target=url,
                                   isp=metric_isp,
                                   region='CCS',
                                   medicion=metric,
                                   type_med=type_med)

        flag.save()
        metric.flags.append(flag)
        metric.save(update_fields=['flags'])

    return True
