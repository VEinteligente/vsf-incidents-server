import logging
from django.db.models.expressions import RawSQL
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

from vsf import conf
from django.db.models import F, Count, Case, When, CharField, Q
from event.models import MutedInput, Target
from measurement.models import Metric, Flag, DNSServer
from plugins.dns.models import DNS
from event.utils import suggestedEvents
from plugins.utils import dict_compare
from measurement.views import send_email_users

SYNCHRONIZE_logger = logging.getLogger('SYNCHRONIZE_logger')
td_logger = logging.getLogger('TRUE_DEBUG_logger')


def web_connectivity_to_dns():
    td_logger.info("Comenzando con web_connectivity en DNS")

    web_connectivity_metrics = Metric.objects.filter(
        test_name='web_connectivity'
    )
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))

        web_connectivity_metrics = web_connectivity_metrics.filter(
            bucket_date__gte=SYNCHRONIZE_DATE
        )

    SYNCHRONIZE_logger.info("Fecha de sincronizacion: %s" % (str(SYNCHRONIZE_DATE)))
    SYNCHRONIZE_logger.info("Total de web_connectivity's en el query: %s" % (str(web_connectivity_metrics.count())))
    td_logger.debug("Fecha de sincronizacion: %s" % (str(SYNCHRONIZE_DATE)))
    td_logger.debug("Total de web_connectivity's en el query: %s" % (str(web_connectivity_metrics.count())))

    web_connectivity_metrics = web_connectivity_metrics.annotate(
        queries=RawSQL(
            "test_keys->'queries'", ()
        ),
        control_resolver=RawSQL(
            "test_keys->'control'", ()
        ),
        dns_consistency=RawSQL(
            "test_keys->'dns_consistency'", ()
        )
    ).prefetch_related(
        'dnss'
    ).values(
        'id',
        'measurement',
        'queries',
        'control_resolver',
        'dnss'
    )

    new_dns = list()
    i=0
    for dns_metric in web_connectivity_metrics:


        cr = {} # Control Resolver information
        try:
            cr['failure'] = dns_metric['control_resolver']['dns']['failure']
        except Exception:
            cr['failure'] = None

        try:
            cr['answers'] = {'addrs': dns_metric['control_resolver']['dns']['addrs']}
        except Exception:
            cr['answers'] = None

        td_logger.debug('Total de queries para la metric %s: %s' %
                        (str(dns_metric['id']), str(len(dns_metric['queries']))))

        for query in dns_metric['queries']:
            try:
                if dns_metric['dnss'] is None:
                    if 'hostname' in query:
                        domain = query['hostname']
                        td_logger.debug("%i - trabajando en metrica %s - dominio %s" % (i, dns_metric['id'], domain))
                        try:
                            target = Target.objects.get(domain=domain, type=Target.DOMAIN)
                        except Target.DoesNotExist:
                            target = Target(domain=domain, type=Target.DOMAIN)
                            target.save()
                            td_logger.info("Creado target dominio %s" % domain)
                        except Target.MultipleObjectsReturned:
                            target = Target.objects.Filter(domain=domain, type=Target.DOMAIN).first()
                    else:
                        target = None

                    inconsistent=None
                    if dns_metric['dns_consistency'] == 'consistent':
                        inconsistent = False
                    elif dns_metric['dns_consistency'] == 'inconsistent':
                        constent = True
                    dns = DNS(
                        metric_id=dns_metric['id'],
                        control_resolver_failure=cr['failure'],
                        control_resolver_answers=cr['answers'],
                        failure=dns_metric['dns_experiment_failure'],
                        answers=dns_metric['answers'],
                        target=target,
                        dns_consistency=dns_metric['dns_consistency'],
                        inconsistent=inconsistent
                    )
                    td_logger.debug("DNS a crear %s" % dns)

                    new_dns.append(dns)
                    td_logger.debug('Answer guardada exitosamente para metric %s' % str(dns_metric['id']))
            except Exception as e:
                SYNCHRONIZE_logger.exception("Fallo en web_connectivity_to_dns, en la metric '%s' con el "
                                         "siguiente mensaje: %s" % (str(dns_metric['measurement']), str(e)))
                td_logger.exception("Fallo en web_connectivity_to_dns, en la metric '%s' con el "
                                "siguiente mensaje: %s" % (str(dns_metric['measurement']), str(e)))
        i += 1
        if i % 1000 == 0:
            # No necesariamente hay 1000 DNSs nuevos
            DNS.objects.bulk_create(new_dns)
            new_dns = list()
            SYNCHRONIZE_logger.debug("Hemos pasado ya %s metrics!" % str(i))
            td_logger.info("Hemos pasado ya %s metrics!" % str(i))
    if new_dns:
        DNS.objects.bulk_create(new_dns)
    td_logger.info("Terminando con web_connectivity en DNS")


def dns_consistency_to_dns():
    # Get all metrics with test_name dns_consistency
    # but only values measurement, test_keys->'queries'
    # and test_keys->'control_resolver'

    td_logger.info("Comenzando con dns_consistency")

    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))

        dns_consistency_metrics = Metric.objects.filter(
            test_name='dns_consistency',
            bucket_date__gte=SYNCHRONIZE_DATE
        ).annotate(
            queries=RawSQL(
                "test_keys->'queries'", ()
            ),
            inconsistent=RawSQL(
                "test_keys->'inconsistent'", ()
            ),
            errors=RawSQL(
                "test_keys->'errors'", ()
            ),
            failures=RawSQL(
                "test_keys->'failures'", ()
            ),
            control_resolver=RawSQL(
                "test_keys->'control_resolver'", ()
            )
        )
    else:
        dns_consistency_metrics = Metric.objects.filter(
            test_name='dns_consistency'
        ).annotate(
            queries=RawSQL(
                "test_keys->'queries'", ()
            ),
            inconsistent=RawSQL(
                "test_keys->'inconsistent'", ()
            ),
            errors=RawSQL(
                "test_keys->'errors'", ()
            ),
            failures=RawSQL(
                "test_keys->'failures'", ()
            ),
            control_resolver=RawSQL(
                "test_keys->'control_resolver'", ()
            )
        )

    SYNCHRONIZE_logger.info("Fecha de sincronizacion: %s" % (str(SYNCHRONIZE_DATE)))
    SYNCHRONIZE_logger.info("Total de dns_consistency's en el query: %s" % (str(dns_consistency_metrics.count())))

    td_logger.debug("Fecha de sincronizacion: %s" % (str(SYNCHRONIZE_DATE)))
    td_logger.debug("Total de dns_consistency's en el query: %s" % (str(dns_consistency_metrics.count())))

    dns_consistency_metrics = dns_consistency_metrics.prefetch_related(
        'dnss'
    ).values(
        'id',
        'measurement',
        'queries',
        'control_resolver',
        'dnss',
        'input',
        'inconsistent',
        'errors',
        'failures',
    )

    # for each dns metric get control resolver and other fields

    new_dns = list()
    for i, dns_metric in enumerate(dns_consistency_metrics):
        # Get control_resolver ip address
        cr_ip = dns_metric['control_resolver'].split(':')[0]

        # Get control_resolver
        cr = {}
        for query in dns_metric['queries']:
            # searching for control resolver
            if query['resolver_hostname'] == cr_ip and dns_metric['input'] == query['hostname']:
                cr['failure'] = query['failure']
                cr['answers'] = query['answers']
                cr['resolver_hostname'] = query['resolver_hostname']

        for query in dns_metric['queries']:
            try:
                if (query['resolver_hostname'] != cr_ip) and (query['query_type'] == 'A'):
                    if dns_metric['dnss'] is None:
                        domain = dns_metric['input']
                        try:
                            target = Target.objects.get(domain=domain, type=Target.DOMAIN)
                        except Target.DoesNotExist:
                            target = Target(domain=domain, type=Target.DOMAIN)
                            target.save()
                        except Target.MultipleObjectsReturned:
                            target = Target.objects.Filter(domain=domain, type=Target.DOMAIN).first()

                        inconsistent=None
                        dns_consistency=''
                        if query['resolver_hostname'] in dns_metric['inconsistent']:
                            inconsistent= True;
                            dns_consistency= 'inconsistent responses'

                        else:
                            try:
                                if (
                                    (dns_metric['errors'][query['resolver_hostname']] == 'no_answer')
                                    and
                                    not(
                                        (dns_metric['control_resolver'] in dns_metric['errors'])
                                        or cr['failure']
                                        or dns_metric['control_resolver'] in dns_metric['failures']
                                    )
                                ):
                                    inconsistent= True;
                                    dns_consistency = 'no_answer'
                                elif (
                                    dns_metric['errors'][query['resolver_hostname']] == 'reverse_match'
                                    and
                                    not(
                                        (dns_metric['control_resolver'] in dns_metric['errors'])
                                        or cr['failure']
                                        or dns_metric['control_resolver'] in dns_metric['failures']
                                    )
                                ):
                                    inconsistent=False
                                    dns_consistency = 'reverse_match'

                                else:
                                    dns_consistency = 'consitent if exists'
                                    inconsistent=False
                                    try:
                                        dns_consistency = dns_metric['errors'][query['resolver_hostname']] + '(Resolver)'
                                    except:
                                        pass
                            except (query['resolver_hostname'], KeyError) as e:
                                inconsistent=False
                                td_logger.info("no resolver hostname in %s: %s" % (str(dns_metric['measurement']), str(e))
                            except Exception as e:
                                    SYNCHRONIZE_logger.exception("Unknown exceptionin %s: %s" % (str(dns_metric['measurement']), str(e))


                        #TODO: remove old deprecated code, here for reference still testing
                        # try:
                        #     # if dns_metric['inconsistent'][resolver_hostname]:
                        #     #     inconsistent= True;
                        #     #     dns_consistency= 'inconsistent responses'
                        # except KeyError:
                        #     try:
                        #         dns_consistency = dns_metric['errors'][resolver_hostname] + '(Resolver)'
                        #         if (dns_metric['errors'][resolver_hostname] == 'no_answer'):
                        #             if:
                        #                 inconsistent= True;
                        #         elif (dns_metric['errors'][resolver_hostname] == 'reverse_match'):
                        #             inconsistent= False;
                        #         else:
                        #             inconsistent= False;
                        #
                        #     except KeyError:
                        #         inconsistent= False;
                        #         dns_consistency= 'consistent responses if exists'

                        if dns_consistency:
                            dns = DNS(
                                metric_id=dns_metric['id'],
                                control_resolver_failure=cr['failure'],
                                control_resolver_answers=cr['answers'],
                                control_resolver_resolver_hostname=cr['resolver_hostname'],
                                failure=query['failure'],
                                answers=query['answers'],
                                resolver_hostname=query['resolver_hostname'],
                                target=target,
                                dns_consistency=dns_consistency,
                                inconsistent=inconsistent
                            )

                        else:
                            dns = DNS(
                                metric_id=dns_metric['id'],
                                control_resolver_failure=cr['failure'],
                                control_resolver_answers=cr['answers'],
                                control_resolver_resolver_hostname=cr['resolver_hostname'],
                                failure=query['failure'],
                                answers=query['answers'],
                                resolver_hostname=query['resolver_hostname'],
                                target=target,
                                dns_consistency=dns_consistency
                            )

                        new_dns.append(dns)
#                         td_logger.debug('DNS consistency guardo exitosamente medicion logica'
#                                        ' perteneciente a la metric %s' % str(dns_metric['id']))
            except Exception as e:
                SYNCHRONIZE_logger.exception("Fallo en dns_consistency_to_dns, en la metric '%s' con el "
                                         "siguiente mensaje: %s" % (str(dns_metric['measurement']), str(e)))
                td_logger.exception("Fallo en dns_consistency_to_dns, en la metric '%s' con el "
                                "siguiente mensaje: %s" % (str(dns_metric['measurement']), str(e)))

        if i % 1000 == 0:
            # No necesariamente hay 1000 DNSs nuevos
            DNS.objects.bulk_create(new_dns)
            new_dns = list()
            SYNCHRONIZE_logger.debug("Saved %i dns logic measurements" % i)
            td_logger.info("Saved %i dns logic measurements" % i)
    if new_dns:
        DNS.objects.bulk_create(new_dns)
    td_logger.info("Terminando con dns_consistency")


def dns_to_flag():
    td_logger.info("Comenzando con dns_to_flag")

    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))
        dnss = DNS.objects.filter(
            metric__bucket_date__gte=SYNCHRONIZE_DATE
        )
    else:
        dnss = DNS.objects.all()

    dnss = dnss.select_related('metric', 'flag')
    i = 0

    td_logger.debug("Total de mediciones DNS a convertir a flags: %s" % str(dnss.count()))

    dns_paginator = Paginator(dnss, 2000)
    for p in dns_paginator.page_range:
        page = dns_paginator.page(p)
        for dns in page.object_list:
            i += 1
            try:
                if dns.flag is None:
                    is_flag = False
                    isp = None
                    if dns.metric.test_name == 'dns_consistency':

                        try:
                            dns_server = DNSServer.objects.get(ip=dns.resolver_hostname)
                            isp = dns_server.isp
                        except (DNSServer.DoesNotExist, KeyError) as e:
                            isp = None

                        if dns.inconsistent:
                            is_flag = True
                            td_logger.debug('%d Found inconsistent DNS (%s) - plugin id: %d - metric=%s %s' %
                                (i, str(dns.dns_consistency), dns.id, str(dns.metric.id), str(dns.target)))
                        # elif (dns.inconsistent==False):
                            # td_logger.debug('%s Found consistent DNS - metric=%s %s' %
                            #     (str(i), str(dns.metric.id), str(dns.target)))
                        elif dns.control_resolver_failure in [None, '']:
                            if dns.failure in [None, '']: # if no failures in measurement
                                if dns.control_resolver_answers:
                                    try:
                                        if dns.metric.test_keys['errors'][dns.resolver_hostname] == "no_answer": # Check for case were the DNS server gave no awnser
                                            is_flag = True
                                            td_logger.debug('%s Found no_awnser flag DNS - metric=%s %s' %
                                                (str(i), str(dns.metric.id), str(dns.target)))

                                    except KeyError:
                                        is_flag = False
                                    '''
                                    #TODO: remove deprecated code
                                        try:
                                            if dns.resolver_hostname in dns.metric.test_keys['inconsistent']: #check for alreadt evaluated logic by ooniprobe
                                            is_flag = True
                                            td_logger.debug('%s Found inconsistent DNS - metric=%s %s' %
                                            (str(i), str(dns.metric.id), str(dns.target)))


                                        except Exception: # if for some reason this fails, lets compare both awnsers (usually a list of dicts, ocacionally it's just a dict)
                                            same = dict_compare(
                                            dns.control_resolver_answers,
                                            dns.answers
                                            )
                                            td_logger.debug('%s Manually comparing metric=%s, same=%s \n %s' %
                                            (str(i), str(dns.metric.id), str(same), str(dns.metric.test_keys['queries'])))
                                            if not same:   #if all elements are not the same
                                            is_flag = True
                                    except Exception: # if for some reason this fails, lets compare both awnsers (usually a list of dicts, ocacionally it's just a dict)
                                        same = dict_compare(
                                            dns.control_resolver_answers,
                                            dns.answers
                                        )
                                        td_logger.debug('%s Manually comparing metric=%s, same=%s \n %s' %
                                            (str(i), str(dns.metric.id), str(same), str(dns.metric.test_keys['queries'])))
                                        if not same:   #if all elements are not the same

                                            is_flag = True

                                         # if [dns.resolver_hostname] == "no_answer" no flag
                                    '''

                    if dns.metric.test_name == 'web_connectivity':

                        isp = dns.metric.probe.isp
                        '''
                        # TODO: Clean this,
                        if (dns.control_resolver_failure is None) and (
                            dns.control_resolver_answers is not None
                        ):
                        '''
                        if dns.inconsistent:
                            is_flag = True

                        elif (dns.inconsistent == False):
                            # TODO: Double check (or ask ooni team) formal definition of consistent to maybe drop this case, or part of it
                            if dns.failure == "no_answer":
                                is_flag = True
                            else:
                                if dns.failure is None and dns.answers is not None:
                                    try:
                                        addr = dns.answers['ipv4']
                                    except Exception:
                                        try:
                                            addr = dns.answers['ipv6']
                                        except Exception:
                                            addr = dns.answers['hostname']
                                    if addr not in dns.control_resolver_answers['addrs']:
                                        is_flag = True

                    # If there is a true flag give 'soft' type
                    if is_flag is True:
                        f_aux = Flag.SOFT
                        # Check if is a muted input
                        muteds = MutedInput.objects.filter(
                            type_med=MutedInput.DNS
                        )
                        muted = muteds.filter(
                            url=dns.metric.input
                        )
                        if muted:
                            f_aux = Flag.MUTED
                    else:
                        f_aux = Flag.NONE

                    flag = Flag(
                        metric_date=dns.metric.bucket_date,
                        metric=dns.metric,
                        target=dns.target,
                        flag=f_aux,
                        isp=isp,
                        plugin_name=dns.__class__.__name__
                    )
                    flag.save()
                    dns.flag = flag
                    dns.save()
#                     td_logger.debug('%s dns convertido a flag=%s, perteneciente a la metric %s' %
#                                    (str(i), str(f_aux), str(dns.metric.id)))
            except Exception as e:
                SYNCHRONIZE_logger.exception("Fallo en dns_to_flag, en el DNS '%s' con el siguiente mensaje: %s" %
                                         (str(dns.id), str(e)))
                td_logger.exception("Fallo en dns_to_flag, en el DNS '%s' con el siguiente mensaje: %s" %
                                (str(dns.id), str(e)))

        td_logger.debug(
            "Saliendo de la pagina %s"
            %
            str(p)
        )

    td_logger.info("Terminando con dns_to_flag")


def soft_to_hard_flags():
    td_logger.info("Comenzando con soft_to_hard_flags")

    ids = Metric.objects.values_list('id', flat=True)
    second_cond = True
    send_email = False

    ##########################################################
    # Evaluating first condition for hard flags
    ##########################################################

    ids_cond_1 = list(reversed(ids))[:conf.LAST_REPORTS_Y1]
    # ids_cond_1 = ids

    ##########################################################
    # Get first all dns soft flags with isp resolver hostname
    ##########################################################
    flags = Flag.objects.filter(
        Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
        dnss__metric__in=ids_cond_1
    ).exclude(
        dnss__resolver_hostname=None
    ).prefetch_related(
        'dnss__metric'
    ).annotate(
        isp=Case(
            default=F('dnss__resolver_hostname'),
            output_field=CharField()
        )

    )

    # Dict than determinate which target/isp has
    # SOFT_FLAG_REPEATED_X1 number of soft flags
    result = flags.values(
        'target',
        'isp'
    ).annotate(
        total_soft=Count(
            Case(
                When(
                    Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
                    then=1
                ),
                output_field=CharField()
            )
        )
    ).filter(total_soft__gte=conf.SOFT_FLAG_REPEATED_X1)

    if result:
        second_cond = False
        for r in result:
            # Get flags to update to hard flags
            flags_to_update_id = flags.filter(
                isp=r['isp'],
                target__id=r['target']
            ).values_list('id', flat=True)

            flags_to_update = Flag.objects.filter(id__in=flags_to_update_id)

            SYNCHRONIZE_logger.info("Se encontro una HARD FLAG en la flag '%s'" % str(flags_to_update.first().id))
            td_logger.warning("Se encontro una HARD FLAG en la flag '%s'" % str(flags_to_update.first().id))

            flags_to_update.update(flag=Flag.HARD)

            for flag in flags_to_update:
                suggestedEvents(flag)
                # Here comes the code to suggest events to each hard flag
                # Here comes the code to suggest hard to another
                # hard flags to create a new event

        send_email = True

    ##########################################################
    # Now all dns soft flags with isp resolver hostname none
    ##########################################################

    flags = Flag.objects.filter(
        Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
        dnss__metric__in=ids_cond_1,
        dnss__resolver_hostname=None
    ).prefetch_related(
        'dnss__metric__probe__isp'
    ).annotate(
        isp=Case(
            default=F('dnss__metric__probe__isp__name'),
            output_field=CharField()
        )
    )

    # Dict than determinate which target/isp has
    # SOFT_FLAG_REPEATED_X1 number of soft flags
    result = flags.values(
        'target',
        'isp'
    ).annotate(
        total_soft=Count(
            Case(
                When(
                    Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
                    then=1
                ),
                output_field=CharField()
            )
        )
    ).filter(total_soft__gte=conf.SOFT_FLAG_REPEATED_X1)

    if result:
        second_cond = False
        for r in result:
            # Get flags to update to hard flags
            flags_to_update_id = flags.filter(
                isp=r['isp'],
                target__id=r['target']
            ).values_list('id', flat=True)

            flags_to_update = Flag.objects.filter(id__in=flags_to_update_id)
            SYNCHRONIZE_logger.info("Se encontro una HARD FLAG en la flag '%s'" % str(flags_to_update.first().id))
            td_logger.warning("Se encontro una HARD FLAG en la flag '%s'" % str(flags_to_update.first().id))

            flags_to_update.update(flag=Flag.HARD)

            for flag in flags_to_update:
                suggestedEvents(flag)
                # Here comes the code to suggest events to each hard flag
                # Here comes the code to suggest hard to another
                # hard flags to create a new event

        send_email = True

    ##########################################################
    # Evaluating Second condition for hard flags
    # Only if First condition doesnt generate any results
    ##########################################################
    if second_cond:
        ids_cond_2 = list(reversed(ids))[:conf.LAST_REPORTS_Y2]

    ##########################################################
    # Get first all dns soft flags with isp resolver hostname
    ##########################################################
        flags = Flag.objects.filter(
            Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
            dnss__metric__in=ids_cond_2
        ).exclude(
            dnss__resolver_hostname=None
        ).prefetch_related(
            'dnss__metric__probe__region'
        ).annotate(
            isp=Case(
                default=F('dnss__resolver_hostname'),
                output_field=CharField()
            ),
            region=Case(
                When(
                    dnss__metric__probe__region__name=str(F(
                        'dnss__resolver_hostname')
                    ),
                    then=F('dnss__metric__probe__region__name')
                ),
                default=None,
                output_field=CharField()
            )

        )

        # Dict than determinate which target/isp has
        # SOFT_FLAG_REPEATED_X1 number of soft flags
        result = flags.values(
            'target',
            'isp',
            'region'
        ).annotate(
            total_soft=Count(
                Case(
                    When(
                        Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
                        then=1
                    ),
                    output_field=CharField()
                )
            )
        ).filter(total_soft__gte=conf.SOFT_FLAG_REPEATED_X2)

        if result:
            for r in result:
                # Get flags to update to hard flags
                flags_to_update_id = flags.filter(
                    isp=r['isp'],
                    target__id=r['target'],
                    region=r['region']
                ).values_list('id', flat=True)

                flags_to_update = Flag.objects.filter(id__in=flags_to_update_id)
                SYNCHRONIZE_logger.info("Se encontro una HARD FLAG en la flag '%s'" % str(flags_to_update.first().id))
                td_logger.debug("Se encontro una HARD FLAG en la flag '%s'" % str(flags_to_update.first().id))
                flags_to_update.update(flag=Flag.HARD)

                for flag in flags_to_update:
                    suggestedEvents(flag)
                    # Here comes the code to suggest events to each hard flag
                    # Here comes the code to suggest hard to another
                    # hard flags to create a new event

            send_email = True

    ##########################################################
    # Now all dns soft flags with isp resolver hostname none
    ##########################################################

        flags = Flag.objects.filter(
            Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
            dnss__metric__in=ids_cond_2,
            dnss__resolver_hostname=None
        ).prefetch_related(
            'dnss__metric__probe__isp'
        ).annotate(
            isp=Case(
                default=F('dnss__metric__probe__isp__name'),
                output_field=CharField()
            ),
            region=Case(
                default=F('dnss__metric__probe__region__name'),
                output_field=CharField()
            )
        )

        # Dict than determinate which target/isp has
        # SOFT_FLAG_REPEATED_X1 number of soft flags
        result = flags.values(
            'target',
            'isp',
            'region'
        ).annotate(
            total_soft=Count(
                Case(
                    When(
                        Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
                        then=1
                    ),
                    output_field=CharField()
                )
            )
        ).filter(total_soft__gte=conf.SOFT_FLAG_REPEATED_X2)

        if result:
            for r in result:
                # Get flags to update to hard flags
                flags_to_update_id = flags.filter(
                    isp=r['isp'],
                    target__id=r['target'],
                    region=r['region']
                ).values_list('id', flat=True)

                flags_to_update = Flag.objects.filter(
                    id__in=flags_to_update_id)
                SYNCHRONIZE_logger.info("Se encontro una HARD FLAG en la flag '%s'" % str(flags_to_update.first().id))
                td_logger.warning("Se encontro una HARD FLAG en la flag '%s'" % str(flags_to_update.first().id))
                flags_to_update.update(flag=Flag.HARD)

                for flag in flags_to_update:
                    suggestedEvents(flag)
                    # Here comes the code to suggest events to each hard flag
                    # Here comes the code to suggest hard to another
                    # hard flags to create a new event

            send_email = True

    ##########################################################
    # Send email to users only if a hard flag was detected
    # Only if First condition doesnt generate any results
    ##########################################################
    if send_email:
        print "Sending email"
        td_logger.debug("Sending email")
        # send_email_users()
    td_logger.info("Terminando con soft_to_hard_flags")


def metric_to_dns():
    print "Start Web_connectivity test"
    SYNCHRONIZE_logger.info("Start Web_connectivity test")
    td_logger.debug("Start Web_connectivity test")

    web_connectivity_to_dns()

    print "End Web_connectivity test"
    SYNCHRONIZE_logger.info("End Web_connectivity test")
    td_logger.debug("End Web_connectivity test")
    print "Start dns_consistency test"
    SYNCHRONIZE_logger.info("Start dns_consistency test")
    td_logger.debug("Start dns_consistency test")

    dns_consistency_to_dns()

    print "End dns_consistency test"
    SYNCHRONIZE_logger.info("End dns_consistency test")
    td_logger.debug("End dns_consistency test")
    print "Start Evaluate DNS Flags"
    SYNCHRONIZE_logger.info("Start Evaluate DNS Flags")
    td_logger.debug("Start Evaluate DNS Flags")

    dns_to_flag()

    print "End Evaluate DNS Flags"
    SYNCHRONIZE_logger.info("End Evaluate DNS Flags")
    td_logger.debug("End Evaluate DNS Flags")
