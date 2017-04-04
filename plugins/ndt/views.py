from plugins.views import PluginTableView, DatatablesView

from django.views import generic
from datetime import datetime
from measurement.models import Metric, Probe, Flag
from models import NDTMeasurement


class NdtTableView(PluginTableView):
    """
    Naked ndt measurement table view
    """
    page_header = "NDT Measurement List"
    page_header_description = "All NDT measurements"
    breadcrumb = ["Measurement", "NDT"]
    titles = [
        'checkbox',
        'annotations',
        'probe',
        'probe isp',
        'probe plan',
        'date',
        'id',
        'report',
        'download',
        'upload',
        'ping',
        'max ping',
        'min ping',
        'timeout',
        '% package loss',
    ]
    url_ajax = '/plugins/ndt/ndt-ajax/'


class NdtAjaxView(DatatablesView):
    """
    Backend for NdtTableView dataTable
    """
    fields = {
        'checkbox': 'id',  # Required
        'annotations': 'metric__annotations',
        'probe': 'metric__probe',
        'probe isp': 'metric__probe__isp',
        'probe plan': 'metric__probe__isp',
        'date': 'date',
        'id': 'id',
        'report': 'metric__report_id',
        'upload': 'upload_speed',
        'download': 'download_speed',
        'ping': 'ping',
        'min ping': 'min_ping',
        'max ping': 'max_ping',
        'timeout': 'timeout',
        '% package loss': 'package_loss',
    }
    queryset = NDTMeasurement.objects.all()

    def get_rows(self, rows):
        """
        Format all rows, and format % of package loss
        :param rows: All rows
        :return: dataTable page formatted
        """
        page_rows = super(NdtAjaxView, self).get_rows(rows)
        for row in page_rows:
            try:
                row['% package loss'] = float(row['% package loss']) * 100
            except TypeError:
                row['% package loss'] = 'Unknown'

            try:
                row['annotations'] = str(row['annotations'])
            except TypeError:
                row['annotations'] = 'Unknown'

        return page_rows


class DailyTestTable(PluginTableView):
    """
    Daily tests averages table view
    """
    page_header = "Daily Speed Test List"
    page_header_description = "Average of all speed test, group by day."
    breadcrumb = ["Measurement", "Speed Test"]
    titles = [
        'Flag',
        'isp',
        'Date',
        'Measurements amount',
        'Download',
        'Upload',
        'Ping',
        'Min ping',
        'Max ping',
        'Time out',
        '% package loss',
    ]
    url_ajax = '/plugins/ndt/speed-test-ajax/'


class SpeedTestAjax(DatatablesView):
    """
    Backend for DailyTestTable dataTable
    """
    fields = {
        'Flag': 'flag',
        'isp': 'ndt__isp',
        'Date': 'ndt__date',
        'Measurements amount': 'ndt__ndt_measurement_count',
        'Download': 'ndt__av_download_speed',
        'Upload': 'ndt__av_upload_speed',
        'Ping': 'ndt__av_ping',
        'Min ping': 'ndt__av_min_ping',
        'Max ping': 'ndt__av_max_ping',
        'Time out': 'ndt__av_timeout',
        '% package loss': 'ndt__av_package_loss',
    }
    queryset = Flag.objects.exclude(ndts=None)

    def get_rows(self, rows):
        """
        Format all rows, and format % of package loss
        :param rows: All rows
        :return: dataTable page formatted
        """
        page_rows = super(SpeedTestAjax, self).get_rows(rows)
        for row in page_rows:
            try:
                row['% package loss'] = float(row['% package loss']) * 100
            except TypeError:
                row['% package loss'] = 'Unknown'

        return page_rows

# --------------------------------------------------------


class PuraPrueba(generic.TemplateView):

    template_name = 'table.html'

    def get(self, request, *args, **kwargs):

        # ----------- Create 200 random probes!

        # isp = ['Cantv', 'Digitel', 'Movistar', 'Inter']
        # country = Country.objects.get(name='Venezuela')
        # for i in range(1000, 1200):
        #     state = State.objects.filter(country=country).order_by('?').first()
        #     p = Probe(
        #         identification=i,
        #         region=state,
        #         country=country,
        #         city='Generic City',
        #         isp=random.choice(isp)
        #     )
        #     try:
        #         p.save()
        #     finally:
        #         print(i)

        # -------------------------------------

        metric = Metric.objects.filter(test_name='ndt').order_by('test_start_time').first()
        print(metric.test_start_time)
        print(metric.annotations['probe'])
        print(datetime(year=2017, month=2, day=10))
        probe = Probe.objects.get(identification='1002')
        dt = NDTMeasurement(
            probe=probe,
            date=datetime(year=2017, month=2, day=10)
        )
        dt.save()
        return super(PuraPrueba, self).get(args, kwargs)
