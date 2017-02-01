import time
from django.db.models import Q

from measurement.models import Metric, Flag, Probe, MetricFlag
from event.models import Url, Event
from event.front.utils import suggestedFlags

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

            m_flag, created = MetricFlag.objects.get_or_create(
                metric_id=metric_sql['id'],
                manual_flag=True,
                target=target.url)

        return True

    except Exception as e:
        print e
        return False


def change_to_manual_flag_and_create_event(metrics_sql):
    """
    Create event from measurements selected in list.

    metrics_sql: list of Object Metric
    """
    flags_event = []
    id_flags = []
    target = ""
    isp = "Unknown"
    metric_flags = []

    for metric_sql in metrics_sql:
        # Get all flags associated with metric_sql object
        flags = Flag.objects.filter(medicion=metric_sql['id'])

        if not flags:
            # Get or Create Url Input
            url, created = Url.objects\
                              .get_or_create(url=metric_sql['input'])

            # Create Manual Flag
            flag = Flag.objects.create(
                manual_flag=True,
                date=metric_sql['measurement_start_time'],
                target=url,
                region='CCS',
                medicion=metric_sql['id'])

            # Save object in database
            flag.save()
            # Add flag to list destinated to associate flags with the new event
            flags_event.append(flag)
            # Add id flag to list destinated to get earliest flag date
            id_flags.append(flag.id)

            target = url

            m_flag, created = MetricFlag.objects.get_or_create(
                metric_id=metric_sql['id'],
                manual_flag=True,
                target=target.url)
        else:
            for flag in flags:
                flags_event.append(flag)
                id_flags.append(flag.id)
                if target == "":
                    target = flag.target

        try:
            annotations = metric_sql['annotations']
            if annotations['probe'] != "":
                probe = Probe.objects.filter(id=annotations['probe'])
                isp = probe.isp
        except Exception:
            isp = "Unknown"

    # create identification for the event (must be unique)
    num_events = Event.objects.count()
    identification = "event_" + str(num_events)
    identification += "_" + time.strftime("%x") + "_" + time.strftime("%X")

    # create event
    event_date = Flag.objects.filter(id__in=id_flags).earliest('date').date
    event = Event(
        isp=isp,
        start_date=event_date,
        target=target,
        type='bloqueo por DNS',
        identification=identification
    )
    event.save()

    # Add flags to events
    for flag in flags_event:
        event.flags.add(flag)

    # Add suggested flags to the event
    suggestedFlags(event)

    return event


def validate_metrics(metrics_sql):
    """
    validate_metrics: validate if all metrics in list have one common input,
    test_name and isp. Also validate if all metrics dont have already an event

    metrics_sql: list of Object Metric
    """
    metric_inputs = []
    metric_test_names = []
    metric_isp = []
    metric_ids = []
    for metric_sql in metrics_sql:
        metric_ids.append(metric_sql['id'])
        metric_inputs.append(metric_sql['input'])
        metric_test_names.append(metric_sql['test_name'])
        try:
            annotations = metric_sql['annotations']
            if annotations['probe'] != "":
                probe = Probe.objects.filter(id=annotations['probe'])
                metric_isp.append(probe.isp)
        except Exception:
            return False

    # This validates if there's one metric with an event
    flags = Flag.objects.filter(
        medicion__in=metric_ids, event__isnull=False).count()
    if flags != 0:
        return False


    # Builds sets of inputs ans test_names.
    # If there is a set with lenght differet
    # to 1, then there most be two differrents
    # inputs or test_names between metrics
    input_set = set([x for x in metric_inputs if metric_inputs.count(x) >= 1])
    test_names_set = set(
        [x for x in metric_test_names if metric_test_names.count(x) >= 1])
    isp_set = set([x for x in metric_isp if metric_isp.count(x) >= 1])

    if (len(input_set) == 1) and (len(test_names_set) == 1):
        if (len(isp_set) <= 1):
            return True
        else:
            return False
    else:
        return False
