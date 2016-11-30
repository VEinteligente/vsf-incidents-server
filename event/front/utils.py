from event.models import Event
from measurement.models import Flag


def suggestedEvents(flag):
    """
    suggestedEvents: Function than assign a given hard flag (parameter)
    to every existing event with same target and isp. This funstion save
    directly to DB and return true when the function finish successfully
    or false when a error happens during the execution of this function
    Args:
        flag: Flag object with a hard flag data
    """
    try:
        # searching for events open ended with same target, same isp,
        # and with associated flags with que same region

        # this filter will return a queryset with duplicate events
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
