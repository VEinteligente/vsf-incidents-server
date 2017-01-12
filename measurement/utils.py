from measurement.models import Metric, Flag
from event.models import Url


def change_to_manual_flag(metric):

    try:

        flags = metric.flags.all()

        print "FLAGS" 
        print flags

        if not flags:
            url, created = Url.objects\
                              .get_or_create(url=metric.input)

            flag = Flag.objects.create(manual_flag=True,
                                       date=metric.measurement_start_time,
                                       target=url,
                                       region='CCS',
                                       medicion=metric)

            flag.save()

        return True

    except Exception as e:
        print e
        return False


def change_to_manual_flag_sql(metric_sql):

    try:

        flags = Flag.objects.filter(medicion=metric_sql['id'])

        if not flags:
            url, created = Url.objects\
                              .get_or_create(url=metric_sql['input'])

            flag = Flag.objects.create(manual_flag=True,
                                       date=metric_sql['measurement_start_time'],
                                       target=url,
                                       region='CCS',
                                       medicion=metric_sql['id'])

            flag.save()

        return True

    except Exception as e:
        print e
        return False
