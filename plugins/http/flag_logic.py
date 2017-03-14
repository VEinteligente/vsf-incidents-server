from django.db.models.expressions import RawSQL
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from measurement.models import Metric
from plugins.http.models import HTTP


def web_connectivity_to_http():
    # Get all metrics with test_name web_connectivity
    # but only values id, measurement, test_keys->'status_code_match',
    # test_keys->'headers_match' and test_keys->'body_length_match'
    SYNCRONIZE_DATE = settings.SYNCRONIZE_DATE
    if SYNCRONIZE_DATE is not None:
        SYNCRONIZE_DATE = make_aware(parse_datetime(settings.SYNCRONIZE_DATE))
        web_connectivity_metrics = Metric.objects.filter(
            test_name='web_connectivity',
            measurement_start_time__gte=SYNCRONIZE_DATE
        ).annotate(
            status_code_match=RawSQL(
                "test_keys->'status_code_match'", ()
            ),
            headers_match=RawSQL(
                "test_keys->'headers_match'", ()
            ),
            body_length_match=RawSQL(
                "test_keys->'body_length_match'", ()
            )
        ).values(
            'id',
            'status_code_match',
            'headers_match',
            'body_length_match'
        )
    else:
        web_connectivity_metrics = Metric.objects.filter(
            test_name='web_connectivity'
        ).annotate(
            status_code_match=RawSQL(
                "test_keys->'status_code_match'", ()
            ),
            headers_match=RawSQL(
                "test_keys->'headers_match'", ()
            ),
            body_length_match=RawSQL(
                "test_keys->'body_length_match'", ()
            )
        ).values(
            'id',
            'status_code_match',
            'headers_match',
            'body_length_match'
        )

    for http_metric in web_connectivity_metrics:
        if (http_metric['status_code_match'] is not None) and (
            http_metric['body_length_match'] is not None) and (
            http_metric['headers_match'] is not None
        ):
            http_exist = HTTP.objects.filter(
                metric_id=http_metric['id']
            ).exists()
            if not http_exist:
                http = HTTP(
                    metric_id=http_metric['id'],
                    status_code_match=http_metric['status_code_match'],
                    headers_match=http_metric['headers_match'],
                    body_length_match=http_metric['body_length_match']
                )
                http.save()


def metric_to_http():
    print "Start Web_connectivity test"
    web_connectivity_to_http()
    print "End Web_connectivity test"
