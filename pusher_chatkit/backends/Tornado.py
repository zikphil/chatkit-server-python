import json
import tornado
import tornado.httpclient

from tornado.concurrent import Future
from pusher_chatkit.client import process_response


class TornadoBackend(object):

    def __init__(self):
        self.http = tornado.httpclient.AsyncHTTPClient()

    def process_request(self, method, endpoint, body=None, token=None):
        headers = {'Content-Type': 'application/json'}
        future = Future()

        if token:
            headers['Authorization'] = 'Bearer {}'.format(token['token'])

        def process_response_future(response):
            if response.exception() is not None:
                future.set_exception(response.exception())

            else:
                result = response.result()
                code = result.code
                body = (result.body or b'').decode('utf8')
                future.set_result(process_response(code, body, result.error))

        request = tornado.httpclient.HTTPRequest(
            endpoint,
            method=method,
            body=json.dumps(body) if body else None,
            headers=headers,
            request_timeout=30)

        response_future = self.http.fetch(request, raise_error=False)
        response_future.add_done_callback(process_response_future)

        return future

