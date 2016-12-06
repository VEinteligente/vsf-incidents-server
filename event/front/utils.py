from event.models import Event
from measurement.models import Flag


def suggestedEvents(flag):
    """
    suggestedEvents: Function than assign a given hard flag (parameter)
    to every existing event with same target and isp. This function save
    directly to DB and return true when the function finish successfully
    or false when a error happens during the execution of this function
    Args:
        flag: Flag object with a hard flag data
    """
    try:
        # get all types of event according the hard flag
        eventTypes = getEventTypes(flag)

        # searching for events open ended with same target, same isp,
        # and with associated flags with que same region

        # this filter will return a queryset with duplicate events
        if eventTypes:
            events = Event.objects.filter(
                isp=flag.isp,
                target=flag.target,
                end_date=None,
                type__in=eventTypes,
                flags__probe__region=flag.probe.region)
        else:
            events = Event.objects.filter(
                isp=flag.isp,
                target=flag.target,
                end_date=None,
                flags__probe__region=flag.probe.region)

        # eliminate duplicate events in queryset
        # defining a set with the queryset
        events = set(events)

        # assign every event in the list as a suggested_event of
        # the hard flag
        for event in events:
            flag.suggested_events.add(event)
        return True
    except Exception:
        return False


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
        # get all regions of all flags associated with the event (parameter)
        regions = []
        for flag in event.suggested_events.all():
            regions.append(flag.probe.region)

        # get all types of flags according the event
        flagTypes = getFlagTypes(event)

        # searching for all unassigned hard flags with same target, same isp,
        # and same region in the list of regions

        # this filter will return a queryset with duplicate flags
        if flagTypes:
            flags = Flag.objects.filter(
                flag=True,
                event=None,
                target=event.target,
                isp=event.isp,
                region__in=regions,
                type_med__in=flagTypes)
        else:
            flags = Flag.objects.filter(
                flag=True,
                event=None,
                target=event.target,
                isp=event.isp,
                region__in=regions)

        # eliminate duplicate flags in queryset
        # defining a set with the queryset
        flags = set(flags)

        # assign every flag in the list as a suggested_event of
        # the event
        for flag in flags:
            event.suggested_events.add(event)
        return True
    except Exception:
        return False


def getFlagTypes(event):
    """
    getFlagTypes: Function than return a list with all flag types according
    to que event (parameter). It can return a empty list[]
    Args:
        event: Event object
    """
    flagTypes = []
    if (event.type == 'bloqueo por DNS'):
        flagTypes.append('DNS')
    if (event.type == 'bloqueo por IP'):
        flagTypes.append('TCP')
    if (event.type == 'falla de dns'):
        flagTypes.append('DNS')
        flagTypes.append('TCP')
    if (event.type == 'Interceptacion de trafico') or (
        event.type == 'alteracion de trafico por intermediarios'
    ):
        flagTypes.append('HTTP')
    return flagTypes


def getEventTypes(flag):
    """
    getEventTypes: Function than return a list with all event types according
    to the flag (parameter). It can return a empty list[]
    Args:
        flag: Flag object
    """
    eventTypes = []
    if (flag.type_med == 'DNS'):
        eventTypes.append('bloqueo por DNS')
        eventTypes.append('falla de dns')
    if (flag.type_med == 'TCP'):
        eventTypes.append('bloqueo por IP')
        eventTypes.append('falla de dns')
    if (flag.type_med == 'HTTP'):
        eventTypes.append('Interceptacion de trafico')
        eventTypes.append('alteracion de trafico por intermediarios')
    return eventTypes
