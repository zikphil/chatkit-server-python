import requests
import json


from pusher_chatkit.client import process_response


class RequestsBackend(object):

    def __init__(self):
        self.http = requests
        self.session = requests.Session()

    def process_request(self, method, endpoint, body=None, token=None):
        headers = {'Content-Type': 'application/json'}

        if token:
            headers['Authorization'] = 'Bearer {}'.format(token['token'])

        resp = self.session.request(
            method,
            endpoint,
            headers=headers,
            data=json.dumps(body) if body else None,
            timeout=30)

        return process_response(resp.status_code, resp.text)
