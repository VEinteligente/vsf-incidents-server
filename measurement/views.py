import json
import threading

import logging

from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db.models import (
    Q,
    Count,
    Case,
    When,
    CharField
)
from django.http import HttpResponse
from django.utils.module_loading import import_module
from django.views import generic

from event.models import (
    Target,
    MutedInput
)
from event.utils import (
    suggestedEvents
)
from measurement.front.views import DBconnection, DNSTestKey
from measurement.utils import copy_from_measurements_to_metrics
from measurement.models import (
    Measurement,
    Flag,
    DNS,
    Metric,
    Probe
)
from vsf import conf
from vsf import settings


def send_email_users():
    """docstring for send_email_users
    Send to all admins an email when hard
    flags are created"""

    # Get users emails
    users_emails = User.objects.exclude(
        Q(email='') |
        Q(email=None)
    ).values_list(
        'email',
        flat=True
    )

    # Send email to each user
    # for email_user in users_emails:

    title = 'Se han calculado nuevos Hard Flag'
    msg = 'Actualmente se han agregado nuevos hard flag '
    msg += ' a la base de datos'

    email = EmailMessage(
        title,
        msg,
        to=users_emails
    )
    email.send()


class UpdateFlagView(generic.UpdateView):
    """docstring for UpdateFlagView"""
    model = Flag

    def get(self, request, *args, **kwargs):

        try:
            # List of 'medicion' of Flags #
            list_dns = self.model.objects.using('default')\
                                         .values_list('medicion', flat=True)\
                                         .order_by('medicion')\
                                         .distinct()

            # Create database object #
            database = DBconnection('titan_db')
            ids = None

            if list_dns:

                ids = '('

                for f in list_dns:
                    if f == list_dns[len(list_dns) - 1]:
                        ids += '\'' + f + '\''
                    else:
                        ids += '\'' + f + '\', '

                ids += ')'

            # Query for dns #
            query_dns = "select id, input, test_keys, measurement_start_time "
            query_dns += "from metrics where test_name='dns_consistency' "

            # Query for TCP flags #
            query_tcp = "select id, input, test_keys, measurement_start_time "
            query_tcp += "from metrics where test_name='web_connectivity' "

            if ids:
                query_dns += " and id not in " + ids
                query_tcp += " and id not in " + ids

            # Results from execute queries #
            print "QUERIESSSSS"
            result_dns = database.db_execute(query_dns)
            result_tcp = database.db_execute(query_tcp)
            #result_dns = None
            #result_tcp = None

            rows_dns = {}
            rows_tcp = {}

            if result_dns:

                rows_dns = result_dns['rows']

            if result_tcp:

                rows_tcp = result_tcp['rows']

            # Update DNS Flags #
            print "DNS"
            #update_dns = []
            update_dns = self.update_dns_flags(rows_dns)

            # Update TCP Flags #
            print "TCP"
            #update_tcp = []
            update_tcp = self.update_tcp_flags(rows_tcp)

            # Update HTTP Flags #
            print "HTTP"
            #update_http = []
            update_http = self.update_http_flags(rows_tcp)

            to_bulk_list = []
            to_bulk_list += update_dns + update_tcp + update_http

            # Update Muted Flags #
            print "MUTED"
            update_muted = self.update_muted_flags()

            # Update Hard Flags #
            print "HARD"
            update_hard = self.update_hard_flags()

            if update_dns and update_tcp and \
               update_http and update_hard and \
               update_muted:

                return HttpResponse(status=200)

            return HttpResponse(status=400)

        except Exception as e:

            print e

            return HttpResponse(status=400)

    def update_dns_flags(self, rows):

        flags = []

        for row in rows:

            # Convert json test_keys into python object
            test_key = DNSTestKey(json.dumps(row['test_keys']))

            # Get public DNS #
            if 'annotations' in row:
                if row['annotations']['probe']:
                    probe = Probe.objects.get(identification=row['annotations']['probe'])
                    dns_isp = probe.isp
            else:
                dns_isp = None

            url, created = Target.objects\
                              .get_or_create(url=row['input'])

            # dns_isp = 'cantv' # POR AHORA
            public_dns = [dns.ip
                          for dns in DNS.objects.filter(public=True)]

            date = row['measurement_start_time']

            # Ignore data from test_key #
            if test_key.ignore_data(dns_isp, public_dns):

                # Get queries #
                queries = test_key.get_queries()

                if not queries[0]['failure'] and queries[0]['answers']:

                    # Get answers #
                    answers = queries[0]['answers']
                    control_resolver = []
                    dns_result = []

                    # Get control resolver from answer_type A #
                    for a in answers:
                        if a['answer_type'] == 'A' and \
                           a['ipv4'] not in control_resolver:
                            control_resolver += [a['ipv4']]

                    # Verify each result from queries with control resolver #
                    for query in queries:

                        dns_name = query['resolver_hostname']

                        # If dns_name is in DNS table, find its isp #
                        if DNS.objects.filter(ip=dns_name).exists():
                            dns_isp = DNS.objects\
                                         .get(ip=dns_name).isp

                        # If query doesn't has failure, then find dns result #
                        # from answer type A and later compare it with control #
                        # resolver #
                        if query['failure']:

                            if not Flag.objects.filter(medicion=row['id'],
                                                       ip=dns_name,
                                                       type_med='DNS').exists():

                                flag = False

                                if dns_isp is None:
                                    dns_isp = 'Unknown'
                                    flag = None

                                flag = Flag.objects.create(medicion=row['id'],
                                                           date=date,
                                                           target=url,
                                                           isp=dns_isp,
                                                           region='CCS',
                                                           ip=dns_name,
                                                           flag=flag,
                                                           type_med='DNS')

                                flag.save(using='default')

                        else:

                            answers = query['answers']

                            for a in answers:
                                if a['answer_type'] == 'A' and \
                                   a['ipv4'] not in dns_result:
                                    dns_result += [a['ipv4']]

                            # If doesn't match, generate soft flag in measurement #
                            # if control_resolver != dns_result:
                            if not all(map(lambda v: v in control_resolver, dns_result)):

                                if not Flag.objects.filter(ip=dns_name,
                                                           medicion=row['id'],
                                                           type_med='DNS').exists():

                                    flag = False

                                    if dns_isp is None:
                                        dns_isp = 'Unknown'
                                        flag = None

                                    flag = Flag.objects.create(ip=dns_name,
                                                               flag=flag,
                                                               date=date,
                                                               target=url,
                                                               isp=dns_isp,
                                                               region='CCS',
                                                               medicion=row['id'],
                                                               type_med='DNS')

                                    m_flag = flag.save(using='default')
                                    flags += [m_flag]

        return flags

    def update_tcp_flags(self, rows):

        flags = []

        for row in rows:

            # Convert json test_keys into python object
            test_key = DNSTestKey(json.dumps(row['test_keys']))
            tcp_connect = test_key.get_tcp_connect()

            date = row['measurement_start_time']
            probe = None

            if 'annotations' in row:
                if row['annotations']['probe']:
                    probe = Probe.objects.get(identification=row['annotations']['probe'])
                    dns_isp = probe.isp
            else:
                dns_isp = None

            url, created = Target.objects\
                              .get_or_create(url=row['input'])

            for tcp in tcp_connect:

                if tcp['status']['blocked']:

                    if not Flag.objects.filter(ip=tcp['ip'],
                                               medicion=row['id'],
                                               type_med='TCP').exists():

                        flag = False

                        if dns_isp is None:
                            dns_isp = 'Unknown'
                            flag = None

                        flag = Flag.objects.create(ip=tcp['ip'],
                                                   flag=flag,
                                                   date=date,
                                                   target=url,
                                                   isp=dns_isp,
                                                   region='CCS',
                                                   medicion=row['id'],
                                                   type_med='TCP')

                        m_flag = flag.save(using='default')
                        flags += [m_flag]

        return flags

    def update_http_flags(self, rows):

        flags = []

        for row in rows:

            # Convert json test_keys into python object
            test_key = DNSTestKey(json.dumps(row['test_keys']))

            date = row['measurement_start_time']

            if 'annotations' in row:
                if row['annotations']['probe']:
                    probe = Probe.objects.get(identification=row['annotations']['probe'])
                    dns_isp = probe.isp
            else:
                dns_isp = None

            url, created = Target.objects\
                              .get_or_create(url=row['input'])

            if not test_key.get_headers_match() and \
               not test_key.get_body_length_match() or \
               not test_key.get_status_code_match():

                if not Flag.objects.filter(ip=test_key.get_client_resolver(),
                                           medicion=row['id'],
                                           type_med='HTTP').exists():

                    flag = False

                    if dns_isp is None:
                        dns_isp = 'Unknown'
                        flag = None

                    flag = Flag.objects.create(ip=test_key.get_client_resolver(),
                                               flag=flag,
                                               date=date,
                                               target=url,
                                               isp=dns_isp,
                                               region='CCS',
                                               medicion=row['id'],
                                               type_med='HTTP')

                    m_flag = flag.save(using='default')
                    flags += [m_flag]

        return flags

    def update_muted_flags(self):

        muted_list = list(MutedInput.objects.values_list('url', flat=True))
        type_list = list(MutedInput.objects.values_list('type_med', flat=True))

        flags = Flag.objects.filter(flag=False,
                                    target__url__in=muted_list,
                                    type_med__in=type_list)

        flags.update(flag=None)

        return True

    def update_hard_flags(self):

        # Evaluating first condition for hard flags
        ids = Metric.objects.values_list('id', flat=True)
        ids = list(reversed(ids))[:conf.LAST_REPORTS_Y1]

        # If send emails when hard flag are created
        send_email = False

        flags = Flag.objects\
                    .filter(medicion__in=ids)

        result = flags\
                     .values('isp',
                             'target',
                             'type_med')\
                     .annotate(total_soft=Count(Case(
                               When(flag=False, then=1),
                               output_field=CharField())))\
                     .filter(total_soft=conf.SOFT_FLAG_REPEATED_X1)

        if result:

            for r in result:
                flags_to_update = flags.filter(isp=r['isp'],
                                               target__url=r['target'],
                                               type_med=r['type_med'])
                # If exist flags to update
                if flags_to_update:
                    send_email = True

                map(self.soft_to_hard_flag, flags_to_update)

                flags_id = list(flags.values_list('medicion', flat=True))
                flags_isp = list(flags.values_list('isp', flat=True))
                flags_url = list(flags.values_list('target__url', flat=True))
                flags_type_med = list(flags.values_list('type_med', flat=True))

        else:

            # Evaluating second condition for hard flags
            ids = Metric.objects.values_list('id', flat=True)
            ids = list(reversed(ids))[:conf.LAST_REPORTS_Y2]

            flags = Flag.objects\
                        .filter(medicion__in=ids)

            result = flags\
                        .values('isp', 'target', 'type_med', 'region')\
                        .annotate(total_soft=Count(Case(
                                  When(flag=False, then=1),
                                  output_field=CharField())))\
                        .filter(total_soft=conf.SOFT_FLAG_REPEATED_X2)

            if result:

                for r in result:
                    flags_to_update = flags.filter(isp=r['isp'],
                                                   target__url=r['target'],
                                                   type_med=r['type_med'],
                                                   region=r['region'])

                    # If exist flags to update
                    if flags_to_update:
                        send_email = True

                    map(self.soft_to_hard_flag, flags_to_update)

                    flags_id = list(flags.values_list('medicion', flat=True))
                    flags_isp = list(flags.values_list('isp', flat=True))
                    flags_url = list(flags.values_list('target__url', flat=True))
                    flags_type_med = list(flags.values_list('type_med', flat=True))
                    flags_region = list(flags.values_list('region', flat=True))

        # If send_email then send emails to users
        if send_email:
            send_email_users()

        return True

    def soft_to_hard_flag(self, flag):
        flag.flag = True
        flag.save(using='default')
        suggestedEvents(flag)


def luigiUpdateFlagTask():
    """
    luigiUpdateFlagTask: Task running by thread to update flags
    """
    global running
    running += 1

    SYNCHRONIZE_logger = logging.getLogger('SYNCHRONIZE_logger')
    td_logger = logging.getLogger('TRUE_DEBUG_logger')

    SYNCHRONIZE_logger.info("comenzo a hacer el hilo")
    td_logger.info("comenzo a hacer el hilo")

    try:
        copy_from_measurements_to_metrics()
    except Exception as e:
        SYNCHRONIZE_logger.exception("Fallo creando metrics con el siguiente mensaje: %s" % str(e))
        td_logger.exception("Fallo creando metrics con el siguiente mensaje: %s" % str(e))
    # ----------------------------------------------
    for module in settings.FLAG_TESTS:

        m = import_module("plugins.%s.flag_logic" % module['module_name'])
        for function in module['functions']:
            try:
                method_to_call = getattr(m, function)
                result = method_to_call()
            except Exception as e:
                SYNCHRONIZE_logger.exception("Fallo en %s.%s con el siguiente mensaje: %s" %
                                         (module['module_name'], str(function), str(e)))
                td_logger.exception("Fallo en %s.%s con el siguiente mensaje: %s" %
                                (module['module_name'], str(function), str(e)))
                
        SYNCHRONIZE_logger.info("termino con %s" % module['module_name'])
        td_logger.info("termino con %s" % module['module_name'])
    # Set SYNCRONIZE_DATE
    if settings.SYNCHRONIZE_DATE is not None:
        measurements_date = Measurement.objects.filter(
            measurement_start_time__gte=settings.SYNCHRONIZE_DATE
        ).latest('measurement_start_time').measurement_start_time
    else:
        measurements_date = Measurement.objects.all().latest(
            'measurement_start_time').measurement_start_time

    SYNCHRONIZE_DATE = str(measurements_date)
    SYNCHRONIZE_logger.info("Last SYNCHRONIZE date: '%s'" % SYNCHRONIZE_DATE)
    td_logger.debug("Last SYNCHRONIZE date: '%s'" % SYNCHRONIZE_DATE)


    # ---------------------------------------------
    running -= 1
    SYNCHRONIZE_logger.info("Termino el hilo")
    td_logger.info("Termino el hilo")


"""
running: Global variable defined to be used by
LuigiUpdateFlagView and luigiUpdateFlagTask
to control than no more than 1 thread to be
running luigiUpdateFlagTask at the same time
"""
running = 0


class LuigiUpdateFlagView(generic.View):
    """
    LuigiUpdateFlagView: View called by Ooni-pipeline which created and
    exclusive thread to update flags.
    """
    def get(self, request, *args, **kwargs):
        SYNCHRONIZE_logger = logging.getLogger('SYNCHRONIZE_logger')
        td_logger = logging.getLogger('TRUE_DEBUG_logger')
        global running
        if running < 1:
            SYNCHRONIZE_logger.info("Running: %s" % str(running))
            td_logger.info("Running: %s" % str(running))
            t = threading.Thread(target=luigiUpdateFlagTask)
            t.start()
        else:
            SYNCHRONIZE_logger.info("Threat already running")
            td_logger.info("Threat already running")
            return HttpResponse("<h1>Luigi is already working!</h1>", status=200)
        return HttpResponse("<h1>Luigi was called!</h1>", status=200)
