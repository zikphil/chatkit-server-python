import json
import tornado
import tornado.httpclient

from tornado.concurrent import Future
from pusher_chatkit.client import process_response


class TornadoBackend(object):

    def __init__(self):
        self.http = tornado.httpclient.AsyncHTTPClient()

    def process_request(self, method, endpoint, body=None, token=None):
        data = body
        headers = {'Content-Type': 'application/json'}
        future = Future()

        headers['Authorization'] = 'Bearer {}'.format(token['token'])

        def process_response_future(response):
            if response.exception() is not None:
                future.set_exception(response.exception())

            else:
                result = response.result()
                code = result.code
                body = (result.body or b'').decode('utf8')
                future.set_result(process_response(code, body))

        request = tornado.httpclient.HTTPRequest(
            endpoint,
            method=method,
            body=json.dumps(data),
            headers=headers,
            request_timeout=30)

        response_future = self.http.fetch(request, raise_error=False)
        response_future.add_done_callback(process_response_future)

        return future

