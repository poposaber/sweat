import json
from dataclasses import is_dataclass, asdict
from .message import Message
from .enums import MessageType, Action
from .errors import SchemaError
from .payloads.auth import Credential
from .payloads.common import EmptyPayload

_PAYLOAD_MAP = {
    Action.LOGIN: Credential, 
    Action.REGISTER: Credential, 
    Action.LOGOUT: EmptyPayload, 
}

def encode(message: Message) -> bytes:
    """Encode a Message object to JSON bytes."""
    # Serialize enums to their value and dataclass payloads to dicts.
    msg_type_str = message.type.value if isinstance(message.type, MessageType) else message.type
    action_str = (
        message.action.value if (message.action is not None and isinstance(message.action, Action)) else message.action
    )

    # Only serialize dataclass instances (not dataclass classes)
    if is_dataclass(message.payload) and not isinstance(message.payload, type):
        payload_obj = asdict(message.payload)
    else:
        payload_obj = message.payload

    obj = {
        "type": msg_type_str,
        "payload": payload_obj,
    }
    if action_str:
        obj["action"] = action_str
    if message.msg_id:
        obj["msg_id"] = message.msg_id
    if message.ok is not None:
        obj["ok"] = message.ok

    return json.dumps(obj).encode("utf-8")


def decode(data: bytes) -> Message:
    """Decode JSON bytes to a Message object."""
    obj = json.loads(data.decode("utf-8"))
    msg_type = MessageType(obj["type"])
    action = Action(obj["action"])
    payload_cls = _PAYLOAD_MAP[action]
    try:
        payload = payload_cls(**obj["payload"])
    except TypeError as e:
        raise SchemaError(f"Invalid payload schema for action {action}: {e}") from e
    
    return Message(
        type=msg_type,
        action=action,
        payload=payload,
        msg_id=obj.get("msg_id"),
        ok=obj.get("ok"),
    )