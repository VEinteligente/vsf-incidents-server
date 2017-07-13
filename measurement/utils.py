import datetime
import logging
import time

from django.conf import settings
from django.core.paginator import Paginator
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from event.models import Target, Event
from event.utils import suggestedFlags
from measurement.models import Metric, Flag, Probe, Measurement


def copy_from_measurements_to_metrics():
    td_logger = logging.getLogger('TRUE_DEBUG_logger')
    SYNCHRONIZE_logger = logging.getLogger('SYNCHRONIZE_logger')
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    SYNCHRONIZE_logger.info("[%s]Starting synchronization" %
                            datetime.datetime.now())

    td_logger.info("[%s]Starting synchronization" % datetime.datetime.now())
    td_logger.debug('comenzando la sincronizacion de metrics entre titan y pandora.')

    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))

        measurements = Measurement.objects.filter(
            measurement_start_time__gte=SYNCHRONIZE_DATE
        ).order_by('measurement_start_time')

        td_logger.info('Synchronize date: %s' % str(SYNCHRONIZE_DATE))
        td_logger.info('Total de metrics desde esa fecha %s' % str(measurements.count()))

    else:
        SYNCHRONIZE_logger.info("[%s] SYNCHRONIZE_DATE is None" %
                                datetime.datetime.now())
        td_logger.info("[%s] SYNCHRONIZE_DATE is None" %
                       datetime.datetime.now())
        measurements = Measurement.objects.all().order_by('measurement_start_time')


# toto dead code
        # measurements_date = Measurement.objects.all().latest(
        #     'measurement_start_time').measurement_start_time

        # descomentar en produccion ^

#         dns_consistency = Measurement.objects.filter(test_name='dns_consistency')[:201000].values_list("id", flat=True)
#         measurements = Measurement.objects.exclude(pk__in=list(dns_consistency))
#         measurements_date = measurements.latest(
#             'measurement_start_time'
#         ).measurement_start_time

    td_logger.info(
        'Hay un total de %s mediciones en titan.' % measurements.count())
    SYNCHRONIZE_logger.info("Start Creating/updating")
    td_logger.debug("Start Creating/updating")

    measurement_paginator = Paginator(measurements, 2000)
#     metric_id_paginator = Paginator(
#         measurements.values_list('id', flat=True), 2000)
    new_metrics = list()
    i = 0
    retry_measurements=list();
    for p in measurement_paginator.page_range:
        page = measurement_paginator.page(p)
#         ids = list(metric_id_paginator.page(p).object_list)
        id_list = list(measurement_paginator.page(p).object_list.values_list('id', flat=True))

        SYNCHRONIZE_logger.info(
            "Page %s of %s" % (str(p), str(measurement_paginator.page_range)))
        td_logger.info(
            "Page %s of %s" % (str(p), str(measurement_paginator.page_range)))

        collisions = Metric.objects.filter(
            measurement__in=id_list).values_list('measurement', flat=True)
            
            
        td_logger.info('Page: %i - items: %i - id_list: %i items- collisions: %i' % (p, len(page), len(id_list), len(collisions)))
        
        for measurement in page.object_list:
            if i==0:
                td_logger.debug('First iteration in page %i' % p)                
            i += 1
            td_logger.debug('current id %s (%s)' % (measurement.id, i))
            page_copied=[]
            if measurement.id not in id_list:
                td_logger.error('!!! Measurement ID not checked for duplicates local database - page: %i, iteration: %i - ID: %s' % (p, i, measurement.id)) 
                SYNCHRONIZE_logger.critical('Remote measurement ID, not checked for existance in local DB for copy. Dading to pile for future copy. ID: %s' % measurement.id)
                retry_measurements.append(measurement)                
                # it's unknown the reason behind this case being so prevalent. about 3/page of 20000 in our datasets. 

            elif measurement.id in page_copied:
                td_logger.error('!!! Duplicated measurement ID in page - page: %i, iteration: %i - ID: %s' % (p, i, measurement.id)) 
#                 continue
#                 td_logger.debug('not already copied in page')

            elif unicode(str(measurement.id), "utf-8") in collisions: #uncetain if this complex casting is necesarry, but its working
                # We don't want to update the metrics that already exists in
                # the database.
#                 collisions.remove(measurement.id)
                td_logger.debug('! Colition found and averted for measurement %s - index on page %i, iteration %i' % (measurement.id, p, i) )                

            else:                    
                td_logger.debug('Metric %s' % i)
                page_copied.append(measurement.id)
                td_logger.debug('not in DB or already copied in page')
                
                
#                 td_logger.debug('Appending to bulk create (on retry) - ID: s' % measurement.id)
    
                obj = Metric(
                    measurement=measurement.id,
                    input=measurement.input,
                    annotations=measurement.annotations,
                    report_id=measurement.report_id,
                    report_filename=measurement.report_filename,
                    options=measurement.options,
                    probe_cc=measurement.probe_cc,
                    probe_asn=measurement.probe_asn,
                    probe_ip=measurement.probe_ip,
                    data_format_version=measurement.data_format_version,
                    test_name=measurement.test_name,
                    test_start_time=make_aware(measurement.test_start_time),
                    measurement_start_time=make_aware(measurement.measurement_start_time),
                    test_runtime=measurement.test_runtime,
                    test_helpers=measurement.test_helpers,
                    test_keys=measurement.test_keys,
                    software_name=measurement.software_name,
                    software_version=measurement.software_version,
                    test_version=measurement.test_version,
                    bucket_date=measurement.bucket_date,
                )
    
                td_logger.debug('Obj created for bulk create (on retry) - ID %s' % measurement.id)
                td_logger.debug('-------------------------------------------------------')
    
                new_metrics.append(obj)

        td_logger.debug(
            "Saliendo de la pagina %s, voy a crear %s metricas."
            %
            (str(p), str(len(new_metrics)))
        )
        Metric.objects.bulk_create(new_metrics)
        td_logger.info('%i metrics created in page %i -index reached: %i' % (len(new_metrics), p, i))
        new_metrics = list()
        
        # testing this code to re/introduce measurements that could not be added becuse of lack of validation / probelms with pagination
        # !!! TO-DO: integrate to the same bulk_create for performace after testing
        if retry_measurements:
            td_logger.info('Retry: %i Metrics to re-evaluate and copy if needed (page %i)' % (len(retry_measurements), p))
            for measurement in retry_measurements:
                try: # Check if metric exists on local DB
                    obj = Metric.objects.get(measurement=measurement.id)
                except Metric.DoesNotExist:  # Copy if it doesn't
                    td_logger.debug('Measurement will be copied on retry - ID: %s' % measurement.id )
        
                    obj = Metric(
                        measurement=measurement.id,
                        input=measurement.input,
                        annotations=measurement.annotations,
                        report_id=measurement.report_id,
                        report_filename=measurement.report_filename,
                        options=measurement.options,
                        probe_cc=measurement.probe_cc,
                        probe_asn=measurement.probe_asn,
                        probe_ip=measurement.probe_ip,
                        data_format_version=measurement.data_format_version,
                        test_name=measurement.test_name,
                        test_start_time=make_aware(measurement.test_start_time),
                        measurement_start_time=make_aware(measurement.measurement_start_time),
                        test_runtime=measurement.test_runtime,
                        test_helpers=measurement.test_helpers,
                        test_keys=measurement.test_keys,
                        software_name=measurement.software_name,
                        software_version=measurement.software_version,
                        test_version=measurement.test_version,
                        bucket_date=measurement.bucket_date,
                    )
        
                    td_logger.debug('Obj created for bulk create (on retry) - ID %s' % measurement.id)
                    td_logger.debug('-------------------------------------------------------')
        
                    new_metrics.append(obj)
                else:
                    td_logger.debug('Measurement will NOT be copied, already existed locally- ID: %s' % measurement.id )
            # After the untested measuremnts are verified for collisions with locsal DB, the measurements not existing locallys will be copied
            td_logger.debug('On Retry: %i metrics will be created, out of %i that needed check)' % (len(new_metrics), len(retry_measurements)))
            Metric.objects.bulk_create(new_metrics)
            td_logger.info('On Retry: %i metrics created (in page %i -index reached: %i)' % (len(new_metrics), p, i))
            SYNCHRONIZE_logger.info('On Retry copied: \n %s)' % str(new_metrics))
            SYNCHRONIZE_logger.info('On Retry NOT copied: \n %s)' % str(set(retry_measurements) - set(new_metrics)))

            new_metrics = list() # clean lists for next iteration
            retry_measurements = list()


    if len(new_metrics) > 0:
        td_logger.warning('%i metrics left over - creating now' % len(new_metrics))
        Metric.objects.bulk_create(new_metrics)

    # settings.SYNCHRONIZE_DATE = str(measurements_date)
    # SYNCHRONIZE_logger.info("Last SYNCHRONIZE date: '%s'" % settings.SYNCHRONIZE_DATE)
    # td_logger.debug("Last SYNCHRONIZE date: '%s'" % settings.SYNCHRONIZE_DATE)


def update_or_create(measurement):
    td_logger = logging.getLogger('TRUE_DEBUG_logger')
    create = True
    try:
        obj = Metric.objects.get(measurement=measurement.id)
    except Metric.DoesNotExist:
        obj = Metric(
            measurement=measurement.id,
        )
    else:
        create = False
        td_logger.error('Esta medicion ya existia y se esta sobreescribiendo en la base de datos: %s'
                        % str(measurement.id))
    obj.input = measurement.input
    obj.annotations = measurement.annotations
    obj.report_id = measurement.report_id
    obj.report_filename = measurement.report_filename
    obj.options = measurement.options
    obj.probe_cc = measurement.probe_cc
    obj.probe_asn = measurement.probe_asn
    obj.probe_ip = measurement.probe_ip
    obj.data_format_version = measurement.data_format_version
    obj.test_name = measurement.test_name
    obj.test_start_time = make_aware(measurement.test_start_time)
    obj.measurement_start_time = make_aware(measurement.measurement_start_time)
    obj.test_runtime = measurement.test_runtime
    obj.test_helpers = measurement.test_helpers
    obj.test_keys = measurement.test_keys
    obj.software_name = measurement.software_name
    obj.software_version = measurement.software_version
    obj.test_version = measurement.test_version
    obj.bucket_date = measurement.bucket_date

    return obj, create


def get_type_med(test_name):
    if test_name == 'dns_consistency':
        return 'DNS'
    elif test_name == 'http_header_field_manipulation' or test_name == 'http_invalid_request_line':
        return 'HTTP'
    elif test_name == 'web_connectivity':
        return 'TCP'
    elif test_name == 'ndt':
        return 'NDT'
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
            url, created = Target.objects\
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

        return True

    except Exception as e:
        print e
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
            url, created = Target.objects\
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
                    url, created = Target.objects\
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

    if (len(input_set) == 1) and (len(test_names_set) == 1):
        if len(isp_set) <= 1:
            return True
        else:
            return "no same isp"
    else:
        return "no same input or test_name"
