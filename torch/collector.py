from webob import exc
from webob.dec import wsgify
from .prometheus import Registry, Counter, Gauge, Summary, Histogram


class PrometheusMetricCollector(object):
    def __init__(self, prefix="", ttl=None):
        self.routes = {
            prefix: self.report,
            prefix + "/": self.report,
            prefix + "/counter": self.counter,
            prefix + "/gauge/inc": self.gauge_inc,
            prefix + "/gauge/dec": self.gauge_dec,
            prefix + "/gauge/set": self.gauge_set,
            prefix + "/summary": self.summary,
            prefix + "/histogram": self.histogram,
            prefix + "/batch": self.batch,
        }
        self.metric_registry = Registry(ttl=ttl)

    @wsgify
    def __call__(self, request):
        try:
            route = self.routes[request.path_info]
        except KeyError:
            raise exc.HTTPNotFound()
        else:
            return route(request)

    def metric_from_request(self, klass, body):
        if klass is Histogram and "buckets" in body:
            metric_family = self.metric_registry.add_metric(
                klass, body["name"], body["description"], buckets=body["buckets"]
            )
        else:
            metric_family = self.metric_registry.add_metric(
                klass, body["name"], body["description"]
            )
        try:
            metric = metric_family.labels(body["labels"])
        except TypeError as ex:
            raise ValueError(ex)
        else:
            return metric

    def batch(self, request):

        op_list = request.json_body
        for op in op_list:
            path = op.path

            if path == "/counter":
                return self._counter(op)
            if path == "/gauge/inc":
                return self._gauge_inc(op)
            if path == "/gauge/dec":
                return self._gauge_dec(op)
            if path == "/gauge/set":
                return self._gauge_set(op)
            if path == "/summary":
                return self._summary(op)
            if path == "/histogram":
                return self._histogram(op)
            if path == "/batch":
                return self._batch(op)

        return exc.HTTPOk()

    def counter(self, request):
        return self._counter(request.json_body)

    def _counter(self, body):
        try:
            metric = self.metric_from_request(Counter, body)
            metric.inc(body["value"])
        except ValueError as ex:
            raise exc.HTTPBadRequest(body=str(ex))
        return exc.HTTPOk()

    def gauge_inc(self, request):
        return self._gauge_inc(request.json_body)

    def _gauge_inc(self, body):
        try:
            metric = self.metric_from_request(Gauge, body)
            metric.inc(body["value"])
        except ValueError as ex:
            raise exc.HTTPBadRequest(body=str(ex))
        return exc.HTTPOk()

    def gauge_dec(self, request):
        return self._gauge_dec(request.json_body)

    def _gauge_dec(body):
        try:
            metric = self.metric_from_request(Gauge, body)
            metric.dec(body["value"])
        except ValueError as ex:
            raise exc.HTTPBadRequest(body=str(ex))
        return exc.HTTPOk()

    def gauge_set(self, request):
        return self._gauge_set(request.json_body)

    def _gauge_set(self, body):
        try:
            metric = self.metric_from_request(Gauge, body)
            metric.set(body["value"])
        except ValueError as ex:
            raise exc.HTTPBadRequest(body=str(ex))
        return exc.HTTPOk()

    def summary(self, request):
        return self._summary(request.json_body)

    def _summary(self, body):
        try:
            metric = self.metric_from_request(Summary, body)
            metric.observe(body["value"])
        except ValueError as ex:
            raise exc.HTTPBadRequest(body=str(ex))
        return exc.HTTPOk()

    def histogram(self, request):
        return self._histogram(request.json_body)

    def _histogram(self, body):
        try:
            metric = self.metric_from_request(Histogram, body)
            metric.observe(body["value"])
        except ValueError as ex:
            raise exc.HTTPBadRequest(body=str(ex))
        return exc.HTTPOk()

    def report(self, request):
        headers = [("Content-type", "text/plain; version=0.0.4; charset=utf-8")]
        response = exc.HTTPOk(headers=headers, body=self.metric_registry.render())
        return response
