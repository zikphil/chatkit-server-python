from enum import Enum
from dataclasses import dataclass, field, InitVar, make_dataclass
from typing import Union
from functools import partial


# region ENUMS
class PayloadKey(str, Enum):
    ATTACHMENT = "attachment"
    CONTENT = "content"
    URL = "url"


class MessageType(str, Enum):
    TEXT = "text/plain"


# endregion


# region Payloads
class Payload:
    key: PayloadKey
    body: Union[str, dict]

    def __init__(self, body):
        self.body = body

    def as_dict(self) -> dict:
        return {self.key.value: self.body}


class InlinePayload(Payload):
    key = PayloadKey.CONTENT


class AttachmentPayload(Payload):
    key = PayloadKey.ATTACHMENT


class UrlPayload(Payload):
    key = PayloadKey.URL


# endregion


class MessagePart:
    type: MessageType
    payload: Payload

    def __init__(self, payload):
        self.payload = self.payload(payload)

    def as_dict(self) -> dict:
        result = {"type": self.type.value}
        result.update(self.payload.as_dict())
        return result


class TextMessage(MessagePart):
    type: MessageType = MessageType.TEXT
    payload = InlinePayload
