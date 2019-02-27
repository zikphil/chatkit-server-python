import json

from pusher_chatkit.exceptions import PusherBadAuth, PusherBadRequest, PusherBadStatus, PusherForbidden
from urllib.parse import urlencode, quote_plus


class PusherChatKitClient(object):

    def __init__(self, backend, instance_locator):
        self.http = backend()
        self.instance_locator = instance_locator.split(':')
        self.scheme = 'https'
        self.host = self.instance_locator[1] + '.pusherplatform.io'
        self.instance_id = self.instance_locator[2]
        self.services = {
            'api': {
                'service_name': 'chatkit',
                'service_version': 'v2'
            },
            'authorizer': {
                'service_name': 'chatkit_authorizer',
                'service_version': 'v2'
            },
            'cursors': {
                'service_name': 'chatkit_cursors',
                'service_version': 'v2'
            }
        }

    def build_endpoint(self, service, api_endpoint, query):
        service_path_fragment = self.services[service]['service_name'] + '/' + self.services[service]['service_version']
        full_path = '{}://{}/services/{}/{}{}'.format(
            self.scheme,
            self.host,
            service_path_fragment,
            self.instance_id,
            api_endpoint
        )
        query = '?' + urlencode(query, quote_via=quote_plus) if query else ""

        return full_path + query

    def get(self, service, endpoint, query=None, **kwargs):
        return self.http.process_request(
            'GET',
            self.build_endpoint(service, endpoint, query),
            kwargs.get('body', None),
            kwargs.get('token', None),
        )

    def put(self, service, endpoint, query=None, **kwargs):
        return self.http.process_request(
            'PUT',
            self.build_endpoint(service, endpoint, query),
            kwargs.get('body', None),
            kwargs.get('token', None),
        )

    def post(self, service, endpoint, query=None, **kwargs):
        return self.http.process_request(
            'POST',
            self.build_endpoint(service, endpoint, query),
            kwargs.get('body', None),
            kwargs.get('token', None),
        )

    def delete(self, service, endpoint, query=None, **kwargs):
        return self.http.process_request(
            'DELETE',
            self.build_endpoint(service, endpoint, query),
            kwargs.get('body', None),
            kwargs.get('token', None),
        )


def process_response(status, body):
    if status >= 200 and status <= 299:
        return json.loads(body)

    elif status == 400:
        raise PusherBadRequest(body)

    elif status == 401:
        raise PusherBadAuth(body)

    elif status == 403:
        raise PusherForbidden(body)

    else:
        raise PusherBadStatus("%s: %s" % (status, body))
