from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.db.models import Q
from event.models import State, Country, ISP, Plan
from measurement.models import Metric, Probe, Flag
from vsf import conf, settings


def soft_to_hard_flags():

    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))

        new_flags = Flag.objects.filter(
            Q(flag=Flag.SOFT,
              metric_date__gte=SYNCHRONIZE_DATE) |
            Q(flag=Flag.HARD,
              metric_date__gte=SYNCHRONIZE_DATE)
        )
    else:
        new_flags = Flag.objects.filter(Q(flag=Flag.SOFT) | Q(flag=Flag.HARD))

    for flag in new_flags:

        all_flags = Flag.objects.filter(
            plugin_name=flag.plugin_name,
            target=flag.target,
            isp=flag.isp
        ).order_by('metric_date')[:conf.LAST_REPORTS_Y1]

        if all_flags.filter(Q(flag=Flag.SOFT) | Q(flag=Flag.HARD)).count() >= conf.SOFT_FLAG_REPEATED_X1:
            all_flags.update(flag=Flag.HARD)
            flag.flag = Flag.HARD
            flag.save()


def dict_compare(d1, d2):
    if not isinstance(d1, list):
        d1 = list(d1)
    if not isinstance(d2, list):
        d2 = list(d2)

    for dict1 in d1:
        if dict1 not in d2:
            return False

    return True
#  TODO need to optimize thiscomparison


def give_probes_to_metrics():
    metrics = Metric.objects.all()
    for metric in metrics:
        probe = Probe.objects.all().order_by('?').first()
        metric.annotations['probe'] = probe.identification
        metric.save()


def create_isps():
    isp1 = ISP(
        name='Cantv'
    )
    isp1.save()
    isp2 = ISP(
        name='Digitel'
    )
    isp2.save()
    isp3 = ISP(
        name='Inter'
    )
    isp3.save()
    isp4 = ISP(
        name='NetUno'
    )
    isp4.save()
    isp5 = ISP(
        name='Movistar'
    )
    isp5.save()


def create_plans():
    isps = ISP.objects.all()
    for isp in isps:
        p1 = Plan(
            name='12Mb',
            isp=isp,
            upload='3Mb',
            download='8Mb'
        )
        p1.save()
        p2 = Plan(
            name='10Mb',
            isp=isp,
            upload='2Mb',
            download='6Mb'
        )
        p2.save()
        p3 = Plan(
            name='6Mb',
            isp=isp,
            upload='1Mb',
            download='3Mb'
        )
        p3.save()
        p4 = Plan(
            name='4Mb',
            isp=isp,
            upload='500Kb',
            download='1Mb'
        )
        p4.save()


def create_probes():

    country = Country.objects.get(name='Venezuela')
    for i in range(1000, 1400):
        state = State.objects.filter(country=country).order_by('?').first()
        isp = ISP.objects.order_by('?').first()
        plan = Plan.objects.filter(isp=isp).order_by('?').first()
        p = Probe(
            identification=i,
            region=state,
            country=country,
            city='Generic City',
            isp=isp,
            plan=plan
        )
        try:
            p.save()
        finally:
            print(i)


def probes_pls():
    create_isps()
    create_plans()
    create_probes()
