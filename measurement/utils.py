from measurement.models import Metric, Flag
from event.models import Url


def change_to_manual_flag_sql(metric_sql):
    """
    Change to Manual Flag.

    metric_sql: Object Metric
    """

    try:

        # Get all flags associated with metric_sql object
        flags = Flag.objects.filter(medicion=metric_sql['id'])

        if not flags:
            # Get or Create Url Input
            url, created = Url.objects\
                              .get_or_create(url=metric_sql['input'])

            # Create Manual Flag
            flag = Flag.objects.create(manual_flag=True,
                                       date=metric_sql['measurement_start_time'],
                                       target=url,
                                       region='CCS',
                                       medicion=metric_sql['id'])

            # Save object in database
            flag.save()

        return True

    except Exception as e:
        print e
        return False
