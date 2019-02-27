# chatkit-server-python

The Unofficial Python server SDK for Pusher Chatkit.

## Installation

```sh
$ pip install pusher-chatkit-server
```

## Usage

```python
from pusher_chatkit import PusherChatKit
from pusher_chatkit.backends import RequestsBackend, TornadoBackend

chatkit = PusherChatKit(
    'instance-locator',
    'api-key',
    RequestsBackend or TornadoBackend
)

# Requests Example
data = chatkit.create_user(...)
print(data)

# Tornado Example
data = await chatkit.create_user(...)
print(data)

```

## Credits
This work is sponsored by [LedgerX](https://ledgerx.com)