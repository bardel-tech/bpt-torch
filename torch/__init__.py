__commit__ = "937e7a362d99b4fbb9e59562de7c7dd05f87e1c8"
__version__ = "0.5.0"
__build__ = ""

import sentry_sdk


def main():

    sentry_sdk.init(
        "https://7d13d430ec1f446f9cea27f89eb02f7a:39e35c3b5a184fe588e9dbff97f32e63@sentry.bardel.ca/12",
        release="bpttorch@" + __version__,
        attach_stacktrace=True,
        send_default_pii=True,
    )

    from gevent.monkey import patch_all

    patch_all()
    import os
    from datetime import timedelta
    from gevent import pywsgi as wsgi
    from .collector import PrometheusMetricCollector

    class QuietWSGIHandler(wsgi.WSGIHandler):
        """WSGIHandler subclass that will not create an access log"""

        def log_request(self, *args):
            pass

    port = int(os.environ["SERVICE_PORT"])
    ttl = timedelta(hours=int(os.environ.get("TORCH_TTL", 24)))
    metrics_prefix = "/metrics"

    application = PrometheusMetricCollector(prefix=metrics_prefix, ttl=ttl)

    httpd = wsgi.WSGIServer(
        ("0.0.0.0", port), application, handler_class=QuietWSGIHandler
    )
    try:
        httpd.serve_forever()
    except:
        httpd.stop()
