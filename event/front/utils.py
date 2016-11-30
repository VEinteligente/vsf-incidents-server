from event.models import Event
from measurement.models import Flag


def suggestedEvents(flag):
    """suggestedEvents: Function than assign a given hard flag (parameter)
    to every existing event with same target and isp. This funstion save
    directly to DB and return true when the function finish successfully
    or false when a error happens during the execution of this function
    Args:
        flag: Flag object"""
    try:

        events = Event.objects.filter(isp=flag.isp, target=flag.target)
        for event in events:
            flag.suggested_events.add(event)
        return True
    except Exception:
        return False
