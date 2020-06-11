import time
import json
from django.db.models import Q

from measurement.models import Metric, Flag, Probe, MetricFlag
from event.models import Url, Event
from event.front.utils import suggestedFlags
from random import randint


def get_type_med(test_name):
    if test_name == 'dns_consistency':
        return 'DNS'
    elif test_name == 'http_header_field_manipulation' or test_name == 'http_invalid_request_line':
        return 'HTTP'
    elif test_name == 'web_connectivity':
        return 'TCP'
    else:
        return 'MED'


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

            type_med = get_type_med(metric_sql['test_name'])

            # Create Manual Flag
            flag = Flag.objects.create(
                manual_flag=True,
                date=metric_sql['measurement_start_time'],
                target=url,
                region='CCS',
                medicion=metric_sql['id'],
                type_med=type_med
            )

            # Save object in database
            flag.save()

            m_flag, created = MetricFlag.objects.get_or_create(
                metric_id=metric_sql['id'],
                manual_flag=True,
                target=url)

        return True

    except Exception as e:
        print (e)
        return False


def change_to_manual_flag_and_create_event(metrics_sql, type_med):
    """
    Create event from measurements selected in list.

    metrics_sql: list of Object Metric
    """
    flags_event = []
    id_flags = []
    target = ""
    isp = "Unknown"

    for metric_sql in metrics_sql:
        # Get all flags associated with metric_sql object
        flags = Flag.objects.filter(medicion=metric_sql['id'])

        if not flags:
            # Get or Create Url Input
            url, created = Url.objects\
                              .get_or_create(url=metric_sql['input'])

            if type_med == "MED":
                type_med = get_type_med(metric_sql['test_name'])

            try:
                probe_id = metric_sql['annotations']['probe']
                probe = Probe.objects.filter(identification=probe_id).first()
                region = probe.region.name
            except Exception:
                region = 'CCS'
            # Create Manual Flag
            flag = Flag.objects.create(
                manual_flag=True,
                date=metric_sql['measurement_start_time'],
                target=url,
                region=region,
                medicion=metric_sql['id'],
                type_med=type_med)

            # Save object in database
            flag.save()
            # Add flag to list destinated to associate flags with the new event
            flags_event.append(flag)
            # Add id flag to list destinated to get earliest flag date
            id_flags.append(flag.id)

            target = url

            # Save objects in remote database if is not already
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

        # Check if metric have a prove assigned to it.
        # If it is get ISP from probe.
        # If not, ISP will be Unknown
        try:
            annotations = metric_sql['annotations']
            if annotations['probe'] != "":
                probe = Probe.objects.filter(
                    identification=annotations['probe']).first()
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
        flag.suggested_events.clear()
        event.flags.add(flag)

    # Add suggested flags to the event
    suggestedFlags(event)

    return event


def change_to_flag_and_create_event(metrics_sql, list_ip, type_med):
    """
    Create event from measurements selected in list.

    metrics_sql: list of Object Metric
    list_ip: list of ['metric_id@ip']
    """
    flags_event = []
    id_flags = []
    target = ""
    isp = "Unknown"
    ip = ""
    list_ip = list_ip.split(",")

    for metric_sql in metrics_sql:

        for metric in list_ip:
            metric = metric.replace("'", "")
            m_ip = metric.split("@")
            if str(m_ip[0]) == str(metric_sql['id']):
                ip = m_ip[1]
                # Get all flags associated with metric_sql object
                flags = Flag.objects.filter(medicion=metric_sql['id'], ip=ip)

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
                        medicion=metric_sql['id'],
                        ip=ip,
                        type_med=type_med)
                    # Save object in database
                    flag.save()
                    
                    # Add flag to list destinated to associate flags with the new event
                    flags_event.append(flag)
                    # Add id flag to list destinated to get earliest flag date
                    id_flags.append(flag.id)

                    target = url

                    # Save objects in remote database if is not already
                    m_flag, created = MetricFlag.objects.get_or_create(
                        metric_id=metric_sql['id'],
                        manual_flag=True,
                        target=target.url,
                        ip=ip,
                        type_med=type_med)

                else:
                    for flag in flags:
                        flags_event.append(flag)
                        id_flags.append(flag.id)
                        if target == "":
                            target = flag.target

                # Check if metric have a prove assigned to it.
                # If it is get ISP from probe.
                # If not, ISP will be Unknown
                try:
                    annotations = metric_sql['annotations']
                    if annotations['probe'] != "":
                        probe = Probe.objects.filter(
                            identification=annotations['probe']).first()
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
        flag.suggested_events.clear()
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
                probe = Probe.objects.filter(
                    identification=annotations['probe']).first()
                metric_isp.append(probe.isp)
        except Exception:
            return "no probe"

    # This validates if there's one metric with an event
    flags = Flag.objects.filter(
        medicion__in=metric_ids, event__isnull=False).count()
    if flags != 0:
        return "already in event"

    # Builds sets of inputs ans test_names.
    # If there is a set with lenght differet
    # to 1, then there most be two differrents
    # inputs or test_names between metrics
    input_set = set([x for x in metric_inputs if metric_inputs.count(x) >= 1])
    test_names_set = set(
        [x for x in metric_test_names if metric_test_names.count(x) >= 1])
    isp_set = set([x for x in metric_isp if metric_isp.count(x) >= 1])
    print ("Pedro sets:")
    print (input_set)
    print (test_names_set)
    print (isp_set)

    if (len(input_set) == 1) and (len(test_names_set) == 1):
        if (len(isp_set) <= 1):
            return True
        else:
            return "no same isp"
    else:
        return "no same input or test_name"


# def add_probe_to_ndt():
#     metrics = Metric.objects.filter(test_name='ndt')
#     for metric in metrics:
#         rand = randint(1000, 1009)
#         metric.annotations['probe'] = str(rand)
#         metric.annotations = json.dumps(metric.annotations)
#         metric.options = json.dumps(metric.options)
#         metric.test_helpers = json.dumps(metric.test_helpers)
#         metric.test_keys = json.dumps(metric.test_keys)
#         metric.save()

