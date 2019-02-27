import jwt

from datetime import datetime
from pusher_chatkit import constants
from pusher_chatkit.backends import RequestsBackend
from pusher_chatkit.client import PusherChatKitClient


class PusherChatKit(object):

    def __init__(self, instance_locator, api_key, backend=RequestsBackend):
        self.client = PusherChatKitClient(backend, instance_locator)
        self.instance_locator = instance_locator
        self.api_key = api_key

    def generate_token(self, **kwargs):
        split_instance_locator = self.instance_locator.split(':')
        split_key = self.api_key.split(':')

        now = int(datetime.now().timestamp())
        claims = {
            'instance': split_instance_locator[2],
            'iss': 'api_keys/{}'.format(split_key[0]),
            'iat': now
        }

        if 'user_id' in kwargs:
            claims['sub'] = kwargs['user_id']

        if 'su' in kwargs and kwargs['su'] is True:
            claims['su'] = True

        claims['exp'] = now + (24 * 60 * 60)

        token = jwt.encode(claims, split_key[1])

        return {
            'token': token.decode('utf-8'),
            'expires_in': 24 * 60 * 60
        }

    #
    # USERS
    #

    def create_user(self, user_id, name, avatar_url=None, custom_data=None):
        if not type(user_id) == str:
            raise Exception('user_id must be a string.')

        return self.client.post(
            'api',
            '/users',
            body={
                'id': user_id,
                'name': name,
                'avatar_url': avatar_url,
                'custom_data': custom_data
            },
            token=self.generate_token(su=True),
        )

    def batch_create_user(self, users):
        if not type(users) == list:
            raise Exception('users must be a list of user objects.')

        return self.client.post(
            'api',
            '/batch_users',
            body=users,
            token=self.generate_token(su=True)
        )

    def update_user(self, user_id, name=None, avatar_url=None, custom_data=None):
        body = {}

        if name:
            body['name'] = name

        if avatar_url:
            body['avatar_url'] = avatar_url

        if custom_data:
            body['custom_data'] = custom_data

        return self.client.put(
            'api',
            '/users/{}'.format(user_id),
            body=body,
            token=self.generate_token(su=True)
        )

    def delete_user(self, user_id):
        return self.client.delete(
            'api',
            '/users/{}'.format(user_id)
        )

    def authenticate_user(self, user_id):
        token = self.generate_token(user_id=user_id)['token']

        return {
            'access_token': token,
            'token_type': 'bearer',
            'expires_in': 24 * 60 * 60
        }

    def get_user(self, user_id):
        return self.client.get(
            'api',
            '/users/{}'.format(user_id),
            token=self.generate_token(su=True)
        )

    def get_users(self, options=None):
        return self.client.get(
            'api',
            '/users',
            query=options,
            token=self.generate_token(su=True)
        )

    def get_users_by_id(self, list_of_ids):
        return self.client.get(
            'api',
            '/users_by_ids',
            query={
                'id': list_of_ids
            },
            token=self.generate_token(su=True)
        )

    #
    # ROOMS
    #

    def create_room(self, name, private=False, user_ids=None, custom_data=None):
        body = {
            'name': name,
            'private': private
        }

        if user_ids:
            body['user_ids'] = user_ids

        if custom_data:
            body['custom_data'] = custom_data

        return self.client.post(
            'api',
            '/rooms',
            body=body,
            token=self.generate_token(su=True)
        )

    def update_room(self, room_id, **kwargs):
        return self.client.put(
            'api',
            '/rooms/{}'.format(room_id),
            body=kwargs,
            token=self.generate_token(su=True)
        )

    def delete_room(self, room_id):
        return self.client.delete(
            'api',
            '/rooms/{}'.format(room_id),
            token=self.generate_token(su=True)
        )

    def get_room(self, room_id):
        return self.client.get(
            'api',
            '/rooms/{}'.format(room_id),
            token=self.generate_token(su=True)
        )

    def get_rooms(self, options=None):
        return self.client.get(
            'api',
            '/rooms',
            body=options,
            token=self.generate_token(su=True)
        )

    def get_user_rooms(self, user_id):
        return self.client.get(
            'api',
            '/users/{}/rooms'.format(user_id),
            token=self.generate_token(su=True)
        )

    def get_user_joinable_rooms(self, user_id):
        return self.client.get(
            'api',
            '/users/{}/rooms'.format(user_id),
            {
                'joinable': True
            },
            token=self.generate_token(su=True)
        )

    def add_users_to_room(self, room_id, list_of_ids):
        return self.client.put(
            'api',
            '/rooms/{}/users/add'.format(room_id),
            body={
                'user_ids': list_of_ids
            },
            token=self.generate_token(su=True)
        )

    def remove_users_to_room(self, room_id, list_of_ids):
        return self.client.put(
            'api',
            '/rooms/{}/users/remove'.format(room_id),
            body={
                'user_ids': list_of_ids
            },
            token=self.generate_token(su=True)
        )

    def get_room_messages(self, room_id, options=None):
        return self.client.get(
            'api',
            '/rooms/{}/messages'.format(room_id),
            options,
            token=self.generate_token(su=True)
        )

    #
    # MESSAGES
    #

    def send_message(self, sender_id, room_id, text):
        return self.client.post(
            'api',
            '/rooms/{}/messages'.format(room_id),
            body={
                'sender_id': sender_id,
                'text': text
            },
            token=self.generate_token(su=True)
        )

    def delete_message(self, message_id):
        return self.client.delete(
            'api',
            '/messages/{}'.format(message_id),
            token=self.generate_token(su=True)
        )

    #
    # ROLES AND PERMISSIONS
    #

    def create_room_role(self, role_name, permissions=None):
        return self.client.post(
            'authorizer',
            '/roles',
            body={
                'scope': constants.ROOM_SCOPE,
                'name': role_name,
                'permissions': permissions if permissions else []
            },
            token=self.generate_token(su=True)
        )

    def create_global_role(self, role_name, permissions=None):
        return self.client.post(
            'authorizer',
            '/roles',
            body={
                'scope': constants.GLOBAL_SCOPE,
                'name': role_name,
                'permissions': permissions if permissions else []
            },
            token=self.generate_token(su=True)
        )

    def delete_room_role(self, role_name):
        return self.client.delete(
            'authorizer',
            '/roles/{}/scope/{}'.format(role_name, constants.ROOM_SCOPE),
            token=self.generate_token(su=True)
        )

    def delete_global_role(self, role_name):
        return self.client.delete(
            'authorizer',
            '/roles/{}/scope/{}'.format(role_name, constants.GLOBAL_SCOPE),
            token=self.generate_token(su=True)
        )

    def assign_room_role_to_user(self, role_name, user_id, room_id):
        return self.client.put(
            'authorizer',
            '/users/{}/roles'.format(user_id),
            body={
                'name': role_name,
                'room_id': room_id
            },
            token=self.generate_token(su=True)
        )

    def assign_global_role_to_user(self, role_name, user_id):
        return self.client.put(
            'authorizer',
            '/users/{}/roles'.format(user_id),
            body={
                'name': role_name
            }
        )

    def remove_room_role_to_user(self, role_name, user_id, room_id):
        return self.client.delete(
            'authorizer',
            '/users/{}/roles'.format(user_id),
            body={
                'name': role_name,
                'room_id': room_id
            },
            token=self.generate_token(su=True)
        )

    def remove_global_role_to_user(self, role_name, user_id):
        return self.client.delete(
            'authorizer',
            '/users/{}/roles'.format(user_id),
            body={
                'name': role_name
            },
            token=self.generate_token(su=True)
        )

    def list_all_roles(self):
        return self.client.get(
            'authorizer',
            '/roles',
            token=self.generate_token(su=True)
        )

    def list_user_roles(self, user_id):
        return self.client.get(
            'authorizer',
            '/users/{}/roles'.format(user_id),
            token=self.generate_token(su=True)
        )

    def list_permissions_for_room_role(self, role_name):
        return self.client.get(
            'authorizer',
            '/roles/{}/scope/{}/permissions'.format(role_name, constants.ROOM_SCOPE),
            token=self.generate_token(su=True)
        )

    def list_permissions_for_global_role(self, role_name):
        return self.client.get(
            'authorizer',
            '/roles/{}/scope/{}/permissions'.format(role_name, constants.GLOBAL_SCOPE),
            token=self.generate_token(su=True)
        )

    def update_permissions_for_room_role(self, role_name, permissions_to_add=None, permissions_to_remove=None):
        return self.client.put(
            'authorizer',
            '/roles/{}/scope/{}/permissions'.format(role_name, constants.ROOM_SCOPE),
            body={
                'permissions_to_add': permissions_to_add,
                'permissions_to_remove': permissions_to_remove
            },
            token=self.generate_token(su=True)
        )

    def update_permissions_for_global_role(self, role_name, permissions_to_add=None, permissions_to_remove=None):
        return self.client.put(
            'authorizer',
            '/roles/{}/scope/{}/permissions'.format(role_name, constants.GLOBAL_SCOPE),
            body={
                'permissions_to_add': permissions_to_add,
                'permissions_to_remove': permissions_to_remove
            },
            token=self.generate_token(su=True)
        )

    #
    # READ CURSORS
    #

    def get_read_cursor(self, user_id, room_id):
        return self.client.get(
            'cursors',
            '/cursors/0/rooms/{}/users/{}'.format(room_id, user_id),
            token=self.generate_token(su=True)
        )

    def set_user_read_cursors(self, user_id, room_id, position):
        return self.client.put(
            'cursors',
            '/cursors/0/rooms/{}/users/{}'.format(room_id, user_id),
            body={
                'position': position
            },
            token=self.generate_token(su=True)
        )

    def get_room_read_cursor(self, room_id):
        return self.client.get(
            'cursors',
            '/cursors/0/rooms/{}'.format(room_id),
            token=self.generate_token(su=True)
        )

    def set_room_read_cursors(self, room_id, position):
        return self.client.put(
            'cursors',
            '/cursors/0/rooms/{}'.format(room_id),
            body={
                'position': position
            },
            token=self.generate_token(su=True)
        )
