from measurement.models import Metric, Probe, Flag, Country, State, ISP


def create_probes():

    country = Country.objects.get(name='Venezuela')
    for i in range(1000, 1400):
        state = State.objects.filter(country=country).order_by('?').first()
        isp = ISP.objects.all().order_by('?').first()
        p = Probe(
            identification=i,
            region=state,
            country=country,
            city='Generic City',
            isp=isp
        )
        try:
            p.save()
        finally:
            print(i)
