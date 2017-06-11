from event.models import Event, Target
from measurement.models import Flag, DNS
from django.db.models import Q


def suggestedEvents(flag):
    """
    suggestedEvents: Function than assign a given flag (parameter)
    to every existing event with same target and isp. This function save
    directly to DB and return true when the function finish successfully
    or false when a error happens during the execution of this function
    Args:
        flag: Flag object with a hard flag data
    """
    # searching for events open ended with same target, same isp,
    # and with associated flags with que same region

    plugin_name = flag.plugin_name
    try:
        dns_server = DNS.objects.get(ip=flag.dnss.resolver_hostname)
        isp = dns_server.isp
    except (Flag.dnss.RelatedObjectDoesNotExist, DNS.DoesNotExist) as e:
        isp = flag.metric.probe.isp

    try:
        region = flag.metric.probe.region
        if isp != flag.metric.probe.isp:
            region = None
    except AttributeError:
        region = None

    # this filter will return a queryset with duplicate events
    events = Event.objects.filter(Q(
        isp=isp,
        target=flag.target,
        region=region,
        plugin_name=plugin_name
    ) | Q(
        isp=isp,
        target=flag.target,
        region=None,
        plugin_name=plugin_name
    ))

    events = events.filter(Q(
        start_date__lte=flag.metric.measurement_start_time,
        end_date__gte=flag.metric.measurement_start_time
    ) | Q(
        start_date__lte=flag.metric.measurement_start_time,
        end_date=None
    ))

    # eliminate duplicate events in queryset
    # defining a set with the queryset
    events = set(events)
    # assign every event in the list as a suggested_event of
    # the hard flag
    flag.suggested_events.add(*events)
    return True


def suggestedFlags(event):
    """
    suggestedFlags: Function than assign to a given event (parameter)
    every unassigned hard flag with same target, isp an region.
    This function save directly to DB and return true
    when the function finish successfully
    or false when a error happens during the execution of this function
    Args:
        event: Event object
    """
    try:

        # searching for all unassigned hard flags with same target, same isp,
        # and same region in the list of regions

        # this filter will return a queryset with duplicate flags
        flags = Flag.objects.filter(
            Q(
                flag=Flag.SOFT,
                event=None,
                target=event.target,
                metric__probe__isp=event.isp,
                plugin_name=event.plugin_name) |
            Q(
                flag=Flag.HARD,
                event=None,
                target=event.target,
                metric__probe__isp=event.isp,
                plugin_name=event.plugin_name)
        )

        # eliminate duplicate flags in queryset
        # defining a set with the queryset
        flags = set(flags)
        # assign every flag in the list as a suggested_event of
        # the event
        for flag in flags:
                event.suggested_flags.add(flag)
        return True
    except Exception as e:
        print "suggestedFlags:" + str(e)
        return False


def get_flag_types(event):
    """
    getFlagTypes: Function than return a list with all flag types according
    to que event (parameter). It can return a empty list[]
    Args:
        event: Event object
    """
    flag_types = []
    if event.type == 'bloqueo por DNS':
        flag_types.append('DNS')
    if event.type == 'bloqueo por IP':
        flag_types.append('TCP')
    if event.type == 'falla de dns':
        flag_types.append('DNS')
        flag_types.append('TCP')
    if (event.type == 'Interceptacion de trafico') or (
        event.type == 'alteracion de trafico por intermediarios'
    ):
        flag_types.append('HTTP')
    return flag_types


def get_event_types(flag):
    """
    getEventTypes: Function than return a list with all event types according
    to the flag (parameter). It can return a empty list[]
    Args:
        flag: Flag object
    """
    event_types = []
    if flag.type_med == 'DNS':
        event_types.append('bloqueo por DNS')
        event_types.append('falla de dns')
    if flag.type_med == 'TCP':
        event_types.append('bloqueo por IP')
        event_types.append('falla de dns')
    if flag.type_med == 'HTTP':
        event_types.append('Interceptacion de trafico')
        event_types.append('alteracion de trafico por intermediarios')
    return event_types
