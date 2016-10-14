from event.front.apps import FrontConfig as EFC
from event.rest.apps import RestConfig as ERC
from measurement.front.apps import FrontConfig as MFC
from measurement.rest.apps import RestConfig as MRC


class MeasurementFrontConfig(MFC):
    label = 'MeasurementFront'


class MeasurementRestConfig(MRC):
    label = 'MeasurementRest'


class EventFrontConfig(EFC):
    label = 'EventFront'


class EventRestConfig(ERC):
    label = 'EventRest'
