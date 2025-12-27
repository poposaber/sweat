import json
import uuid
from dataclasses import dataclass, asdict
from .enums import MessageType, Action
from typing import Optional

class Message:
    def __init__(self, *, type: MessageType, payload, action: Action, msg_id: Optional[str]=None, ok: Optional[bool]=None, error: Optional[str]=None):
        self.type = type
        self.action = action
        self.payload = payload
        self.msg_id = msg_id
        self.ok = ok
        self.error = error

    @classmethod
    def request(cls, action: Action, payload):
        return cls(
            type=MessageType.REQUEST,
            action=action,
            payload=payload,
            msg_id=str(uuid.uuid4()),
        )

    @classmethod
    def response(cls, action: Action, payload, *, msg_id: Optional[str]=None, ok: Optional[bool]=True, error: Optional[str]=None):
        """Convenience constructor for a response message.

        - action: corresponding `Action` for routing/decoding
        - payload: response payload (dataclass or dict)
        - msg_id: optional correlation id (e.g., same as request's id)
        - ok: operation success flag (defaults to True)
        - error: optional error message
        """
        return cls(
            type=MessageType.RESPONSE,
            action=action,
            payload=payload,
            msg_id=msg_id,
            ok=ok,
            error=error,
        )
    
    @classmethod
    def event(cls, action: Action, payload):
        return cls(
            type=MessageType.EVENT,
            action=action,
            payload=payload,
        )

    # def to_json(self) -> bytes:
    #     if not is_dataclass(self.payload):
    #         raise TypeError("payload must be dataclass")

    #     obj = {
    #         "type": self.type.value,
    #         "payload": asdict(self.payload),
    #     }

    #     if self.action:
    #         obj["action"] = self.action.value
    #     if self.req_id:
    #         obj["req_id"] = self.req_id
    #     if self.ok is not None:
    #         obj["ok"] = self.ok

    #     return json.dumps(obj).encode("utf-8")