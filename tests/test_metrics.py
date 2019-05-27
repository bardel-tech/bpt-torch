import mock

from bpttorch.client import MetricsClient


@mock.patch("urllib2.urlopen")
def test_metrics_client_inc_gauge_buffer(mocked_open):
    client = MetricsClient("http://dummy.url.com")
    client.add_metric("test_metric", "description")

    for _ in range(99):
        client.inc_counter("test_metric", "label")
        mocked_open.assert_not_called()

    client.inc_counter("test_metric", "label")
    mocked_open.assert_called_once()
