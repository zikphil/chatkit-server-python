import jwt

from datetime import datetime
from pusher_chatkit import constants
from pusher_chatkit.backends import RequestsBackend
from pusher_chatkit.client import PusherChatKitClient


class PusherChatKit(object):

    def __init__(self, instance_locator, api_key, backend=RequestsBackend):
        """
        Instantiate a new PusherChatKit object.

        :param instance_locator: Instance Locator for your ChatKit Instance.
        :param api_key: API Key of your ChatKit Instance.
        :param backend: Backend object you wish to use.
        """
        self.client = PusherChatKitClient(backend, instance_locator)
        self.instance_locator = instance_locator
        self.api_key = api_key

    #
    # TOKENS
    #

    def generate_token(self, user_id=None, su=None):
        """
        Generates token to communicate with the pusher platform.

        :param user_id: Id of the user to generate the token for.
        :param su: Boolean to generate a sudo token.

        :return: dict including the token and expiration time.
        """
        split_instance_locator = self.instance_locator.split(':')
        split_key = self.api_key.split(':')

        now = int(datetime.now().timestamp())
        claims = {
            'instance': split_instance_locator[2],
            'iss': 'api_keys/{}'.format(split_key[0]),
            'iat': now
        }

        if user_id:
            claims['sub'] = user_id

        if su and su is True:
            claims['su'] = True

        claims['exp'] = now + (24 * 60 * 60)

        token = jwt.encode(claims, split_key[1])

        return {
            'token': token.decode('utf-8'),
            'expires_in': 24 * 60 * 60
        }

    def authenticate_user(self, user_id):
        """
        Generate a user token that can be used by ChatKit clients.

        :param user_id: Id of the user.

        :return: Token dict.
        """
        token = self.generate_token(user_id=user_id)['token']

        return {
            'access_token': token,
            'token_type': 'bearer',
            'expires_in': 24 * 60 * 60
        }

    #
    # USERS
    #

    def create_user(self, user_id, name, avatar_url=None, custom_data=None):
        """
        Create a new user on the platform.

        :param user_id: User id assigned to the user in your app.
        :param name: Name of the new user.
        :param avatar_url: A link to the user’s photo/image.
        :param custom_data: Custom data that may be associated with a user.

        :return: New User object (dict)
        """

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
        """
        Create multiple users in a single request.

        :param users: List of user objects to create.

        :return: List of New User objects dicts.
        """
        if not type(users) == list:
            raise Exception('users must be a list of user objects.')

        return self.client.post(
            'api',
            '/batch_users',
            body=users,
            token=self.generate_token(su=True)
        )

    def update_user(self, user_id, name=None, avatar_url=None, custom_data=None):
        """
        Updates an existing user on the platform.

        :param user_id: User id assigned to the user in your app.
        :param name: Name of the new user.
        :param avatar_url: A link to the user’s photo/image.
        :param custom_data: Custom data that may be associated with a user.

        :return: Updated User object (dict)
        """
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
        """
        Deletes an existing user on the platform.

        :param user_id: User id assigned to the user in your app.

        :return: boolean for success status.
        """
        return self.client.delete(
            'api',
            '/users/{}'.format(user_id),
            token=self.generate_token(su=True)
        )

    def get_user(self, user_id):
        """
        Retrieves a user from the platform.

        :param user_id: User id assigned to the user in your app.

        :return: User object (dict)
        """
        return self.client.get(
            'api',
            '/users/{}'.format(user_id),
            token=self.generate_token(su=True)
        )

    def get_users(self, from_ts=None, limit=None):
        """
        Retrieves many users from the platform.

        :param from_ts: Timestamp (inclusive) from which users with a more recent created_at should be returned.
        :param limit: limit of users to return. must be between1 and 100. If omitted will default to 20.

        :return: List of User objects (dict)
        """
        params = {}

        if from_ts:
            params['from_ts'] = from_ts

        if limit:
            params['limit'] = limit

        return self.client.get(
            'api',
            '/users',
            query=params,
            token=self.generate_token(su=True)
        )

    def delete_all_users(self):
        """
        Loops through all users on the platform and deletes them all.

        :return: True if successful, Exception if not.
        """
        while True:

            batch = self.get_users(limit=100)

            if not batch:
                break

            for user in batch:
                self.delete_user(user['id'])

        return True

    def get_users_by_id(self, list_of_ids):
        """
        Retrieves several users using their ids.

        :param list_of_ids: List of user id strings.

        :return: List of User objects (dict)
        """
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

    def create_room(self, name, creator_id, private=False, user_ids=None, custom_data=None):
        """
        Creates a new chat room.

        :param name: Represents the name with which the room is identified.
        :param creator_id: Id of the user we will use to create this room.
        :param private: Indicates if a room should be private or public. By default, it is public.
        :param user_ids: If you wish to add users to the room at the point of creation, you may provide their user IDs.
        :param custom_data: Custom data that will be associated with the Room.

        :return: New Room object (dict)
        """
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
            token=self.generate_token(user_id=creator_id)
        )

    def update_room(self, room_id, name=None, private=False, custom_data=None):
        """
        Updates an existing chat room.

        :param room_id: Id of the room.
        :param name: Represents the name with which the room is identified.
        :param private: Indicates if a room should be private or public. By default, it is public.
        :param custom_data: Custom data that will be associated with the Room.

        :return: Updated Room object (dict)
        """
        body = {}

        if name:
            body['name'] = name

        if private:
            body['private'] = private

        if custom_data:
            body['custom_data'] = custom_data

        return self.client.put(
            'api',
            '/rooms/{}'.format(room_id),
            body=body,
            token=self.generate_token(su=True)
        )

    def delete_room(self, room_id):
        """
        Deletes an existing chat room.

        :param room_id: Id of the room.

        :return: boolean for success status.
        """
        return self.client.delete(
            'api',
            '/rooms/{}'.format(room_id),
            token=self.generate_token(su=True)
        )

    def get_room(self, room_id):
        """
        Retrieves a chat room from the platform.

        :param room_id: Id of the room.

        :return: Room object (dict)
        """
        return self.client.get(
            'api',
            '/rooms/{}'.format(room_id),
            token=self.generate_token(su=True)
        )

    def get_rooms(self, from_id=None, include_private=False):
        """
        Retrieves many rooms from the platform.

        :param from_id: ID (exclusive) from which rooms with larger IDs should be returned.
        :param include_private: If `true` will also return private rooms present in the instance.

        :return: List of Room objects (dict)
        """
        params = {}

        if from_id:
            params['from_id'] = from_id

        if include_private:
            params['include_private'] = include_private

        return self.client.get(
            'api',
            '/rooms',
            body=params,
            token=self.generate_token(su=True)
        )

    def get_user_rooms(self, user_id):
        """
        Retrieves the rooms a user has access to view.

        :param user_id: Id of the user.

        :return: List of Room objects (dict)
        """
        return self.client.get(
            'api',
            '/users/{}/rooms'.format(user_id),
            token=self.generate_token(su=True)
        )

    def get_user_joinable_rooms(self, user_id):
        """
        Retrieves the rooms a user has access to join.

        :param user_id: Id of the user.

        :return: List of Room objects (dict)
        """
        return self.client.get(
            'api',
            '/users/{}/rooms'.format(user_id),
            {
                'joinable': True
            },
            token=self.generate_token(su=True)
        )

    def add_users_to_room(self, room_id, list_of_ids):
        """
        Adds multiple users to a chat room.

        :param room_id: Id of the room.
        :param list_of_ids: List of user IDs to add to the room.

        :return: boolean for success status.
        """
        return self.client.put(
            'api',
            '/rooms/{}/users/add'.format(room_id),
            body={
                'user_ids': list_of_ids
            },
            token=self.generate_token(su=True)
        )

    def remove_users_to_room(self, room_id, list_of_ids):
        """
        Removes multiple users to a chat room.

        :param room_id: Id of the room.
        :param list_of_ids: List of user IDs to remove to the room.

        :return: boolean for success status.
        """
        return self.client.put(
            'api',
            '/rooms/{}/users/remove'.format(room_id),
            body={
                'user_ids': list_of_ids
            },
            token=self.generate_token(su=True)
        )

    def get_room_messages(self, room_id, initial_id=None, limit=None, direction=None):
        """
        Retrieves messages for a given room.

        :param room_id: Id of the room.
        :param initial_id: Starting id of the range of messages (non-inclusive).
        :param limit: Number of messages to return. If left empty, the limit is set to 20 by default.
        :param direction: Order of messages - one of 'newer' or 'older'.

        :return: List of Message objects (dict)
        """
        params = {}

        if initial_id:
            params['initial_id'] = initial_id

        if limit:
            params['limit'] = limit

        if direction:
            params['direction'] = direction

        return self.client.get(
            'api',
            '/rooms/{}/messages'.format(room_id),
            params,
            token=self.generate_token(su=True)
        )

    #
    # MESSAGES
    #

    def send_message(self, sender_id, room_id, text, attachment=None):
        """
        Sends a message in a chat room.

        :param sender_id: Id of the User sending the message.
        :param room_id: Id of the Room to send the message into.
        :param text: Message text.
        :param attachment: Attachment to send alongside the message.

        :return: message_id if successful.
        """
        return self.client.post(
            'api',
            '/rooms/{}/messages'.format(room_id),
            body={
                'sender_id': sender_id,
                'text': text,
                'attachment': attachment
            },
            token=self.generate_token(su=True)
        )

    def delete_message(self, message_id):
        """
        Deletes a message in a chat room.

        :param message_id: Id of the message to delete.

        :return: boolean for success status.
        """
        return self.client.delete(
            'api',
            '/messages/{}'.format(message_id),
            token=self.generate_token(su=True)
        )

    #
    # ROLES AND PERMISSIONS
    #

    def create_room_role(self, role_name, permissions=None):
        """
        Create a new role within a specific room only.

        :param role_name: Name of the new role.
        :param permissions: Permissions assigned to the role.

        :return: None
        """
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
        """
        Create a new global role.

        :param role_name: Name of the new role.
        :param permissions: Permissions assigned to the role.

        :return: None
        """
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
        """
        Deletes a room-specific role.

        :param role_name: Name of the new role.

        :return: None
        """
        return self.client.delete(
            'authorizer',
            '/roles/{}/scope/{}'.format(role_name, constants.ROOM_SCOPE),
            token=self.generate_token(su=True)
        )

    def delete_global_role(self, role_name):
        """
        Deletes a global role.

        :param role_name: Name of the new role.

        :return: None
        """
        return self.client.delete(
            'authorizer',
            '/roles/{}/scope/{}'.format(role_name, constants.GLOBAL_SCOPE),
            token=self.generate_token(su=True)
        )

    def assign_room_role_to_user(self, role_name, user_id, room_id):
        """
        Assigns a room-specific role to a user.

        :param role_name: Name of the new role.
        :param user_id:  Id of the user.
        :param room_id: Id of the room.

        :return: None
        """
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
        """
        Assigns a global role to a user.

        :param role_name: Name of the new role.
        :param user_id:  Id of the user.

        :return: None
        """
        return self.client.put(
            'authorizer',
            '/users/{}/roles'.format(user_id),
            body={
                'name': role_name
            }
        )

    def remove_room_role_to_user(self, role_name, user_id, room_id):
        """
        Removes a room-specific role to a user.

        :param role_name: Name of the new role.
        :param user_id:  Id of the user.
        :param room_id: Id of the room.

        :return: None
        """
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
        """
        Removes a global role to a user.

        :param role_name: Name of the new role.
        :param user_id:  Id of the user.

        :return: None
        """
        return self.client.delete(
            'authorizer',
            '/users/{}/roles'.format(user_id),
            body={
                'name': role_name
            },
            token=self.generate_token(su=True)
        )

    def list_all_roles(self):
        """
        Lists all roles on the platform.

        :return: List of Role objects (dict)
        """
        return self.client.get(
            'authorizer',
            '/roles',
            token=self.generate_token(su=True)
        )

    def list_user_roles(self, user_id):
        """
        List all roles assigned to a user.

        :param user_id: Id of the user.

        :return: List of Role objects (dict)
        """
        return self.client.get(
            'authorizer',
            '/users/{}/roles'.format(user_id),
            token=self.generate_token(su=True)
        )

    def list_permissions_for_room_role(self, role_name):
        """
        Retrieves a list of permissions for a room-specific role.

        :param role_name: Name of the role.

        :return: List of permissions (string)
        """
        return self.client.get(
            'authorizer',
            '/roles/{}/scope/{}/permissions'.format(role_name, constants.ROOM_SCOPE),
            token=self.generate_token(su=True)
        )

    def list_permissions_for_global_role(self, role_name):
        """
        Retrieves a list of permissions for a global role.

        :param role_name: Name of the role.

        :return: List of permissions (string)
        """
        return self.client.get(
            'authorizer',
            '/roles/{}/scope/{}/permissions'.format(role_name, constants.GLOBAL_SCOPE),
            token=self.generate_token(su=True)
        )

    def update_permissions_for_room_role(self, role_name, permissions_to_add=None, permissions_to_remove=None):
        """
        Updates permissions for a room-specific role.

        :param role_name: Name of the role.
        :param permissions_to_add: List of permissions to add.
        :param permissions_to_remove: List of permissions to remove.

        :return: Role object (dict)
        """
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
        """
        Updates permissions for a global role.

        :param role_name: Name of the role.
        :param permissions_to_add: List of permissions to add.
        :param permissions_to_remove: List of permissions to remove.

        :return: Role object (dict)
        """
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
        """
        Retrieves a read cursor for a user in a chat room.

        :param user_id: Id of the User.
        :param room_id: Id of the Room.

        :return: Cursor object (dict) or None
        """
        return self.client.get(
            'cursors',
            '/cursors/0/rooms/{}/users/{}'.format(room_id, user_id),
            token=self.generate_token(su=True)
        )

    def set_user_read_cursors(self, user_id, room_id, position):
        """
        Sets a read cursor for a user in a chat room.

        :param user_id: Id of the User.
        :param room_id: Id of the Room.
        :param position: The message ID that the user has read up to

        :return: None
        """
        return self.client.put(
            'cursors',
            '/cursors/0/rooms/{}/users/{}'.format(room_id, user_id),
            body={
                'position': position
            },
            token=self.generate_token(su=True)
        )

    def get_room_read_cursor(self, room_id):
        """
        Retrieves all the user cursors for a chat room.

        :param room_id: Id of the Room.

        :return: List of Cursor objects (dict)
        """
        return self.client.get(
            'cursors',
            '/cursors/0/rooms/{}'.format(room_id),
            token=self.generate_token(su=True)
        )

    def get_user_read_cursor(self, user_id):
        """
        Retrieves all the user cursors for all chat room.

        :param user_id: Id of the User.

        :return: List of Cursor objects (dict)
        """
        return self.client.get(
            'cursors',
            '/cursors/0/users/{}'.format(user_id),
            token=self.generate_token(su=True)
        )
