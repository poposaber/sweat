import json
import base64
import typing
from dataclasses import is_dataclass, asdict
from .message import Message
from .enums import MessageType, Action
from .errors import SchemaError
from .payloads.auth import Credential
from .payloads.common import EmptyPayload
# from .payloads.game import (UploadGameChunkPayload, UploadGameFinishPayload, UploadGameInitPayload, UploadGameInitResponsePayload, 
#                             FetchMyWorksResponsePayload, 
#                             FetchGameCoverPayload, FetchGameCoverResponsePayload, 
#                             FetchStorePayload, FetchStoreResponsePayload, 
#                             FetchGameDetailPayload, FetchGameDetailResponsePayload, 
#                             DownloadGameInitPayload, DownloadGameChunkPayload, DownloadGameFinishPayload, DownloadGameInitResponsePayload, DownloadGameChunkResponsePayload)
# from .payloads.room import (CreateRoomPayload, CreateRoomResponsePayload,
#                             LeaveRoomPayload, 
#                             CheckMyRoomResponsePayload, 
#                             FetchRoomListResponsePayload)
from .payloads.game import *
from .payloads.room import *

from .payloads.events import *

_PAYLOAD_MAP = {
    Action.LOGIN: Credential, 
    Action.REGISTER: Credential, 
    Action.LOGOUT: EmptyPayload,
    Action.UPLOAD_GAME_INIT: UploadGameInitPayload,
    Action.UPLOAD_GAME_CHUNK: UploadGameChunkPayload,
    Action.UPLOAD_GAME_FINISH: UploadGameFinishPayload,
    Action.FETCH_MY_WORKS: EmptyPayload,
    Action.FETCH_STORE: FetchStorePayload,
    Action.FETCH_GAME_COVER: FetchGameCoverPayload,
    Action.FETCH_GAME_DETAIL: FetchGameDetailPayload,
    Action.DOWNLOAD_GAME_INIT: DownloadGameInitPayload,
    Action.DOWNLOAD_GAME_CHUNK: DownloadGameChunkPayload,
    Action.DOWNLOAD_GAME_FINISH: DownloadGameFinishPayload,
    Action.CREATE_ROOM: CreateRoomPayload,
    Action.LEAVE_ROOM: EmptyPayload,
    Action.CHECK_MY_ROOM: EmptyPayload,
    Action.FETCH_ROOM_LIST: EmptyPayload,
    Action.ROOM_CREATED: RoomCreatedEventPayload, 
    Action.ROOM_REMOVED: RoomRemovedEventPayload,
    Action.ROOM_UPDATED: RoomUpdatedEventPayload,
    Action.MY_ROOM_UPDATED: MyRoomUpdatedEventPayload,
}

_RESPONSE_PAYLOAD_MAP = {
    Action.UPLOAD_GAME_INIT: UploadGameInitResponsePayload,
    Action.UPLOAD_GAME_CHUNK: EmptyPayload,
    Action.FETCH_MY_WORKS: FetchMyWorksResponsePayload,
    Action.FETCH_STORE: FetchStoreResponsePayload,
    Action.FETCH_GAME_COVER: FetchGameCoverResponsePayload,
    Action.FETCH_GAME_DETAIL: FetchGameDetailResponsePayload,
    Action.DOWNLOAD_GAME_INIT: DownloadGameInitResponsePayload,
    Action.DOWNLOAD_GAME_CHUNK: DownloadGameChunkResponsePayload,
    Action.CREATE_ROOM: CreateRoomResponsePayload,
    Action.CHECK_MY_ROOM: CheckMyRoomResponsePayload,
    Action.FETCH_ROOM_LIST: FetchRoomListResponsePayload,
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
    if message.error:
        obj["error"] = message.error

    def json_default(o):
        if isinstance(o, bytes):
            return base64.b64encode(o).decode('ascii')
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    return json.dumps(obj, default=json_default).encode("utf-8")


def decode(data: bytes) -> Message:
    """Decode JSON bytes to a Message object."""
    obj = json.loads(data.decode("utf-8"))
    msg_type = MessageType(obj["type"])
    action = Action(obj["action"])
    
    if msg_type == MessageType.RESPONSE and action in _RESPONSE_PAYLOAD_MAP:
        payload_cls = _RESPONSE_PAYLOAD_MAP[action]
    else:
        payload_cls = _PAYLOAD_MAP.get(action, EmptyPayload)

    try:
        # Handle EmptyPayload special case (it has no fields)
        if payload_cls is EmptyPayload:
            payload = EmptyPayload()
        else:
            payload_dict = obj["payload"]
            # Convert base64 strings back to bytes based on type hints
            type_hints = typing.get_type_hints(payload_cls)
            for field_name, field_type in type_hints.items():
                if field_type == bytes and field_name in payload_dict:
                    val = payload_dict[field_name]
                    if isinstance(val, str):
                        payload_dict[field_name] = base64.b64decode(val)
            
            payload = payload_cls(**payload_dict)
    except TypeError as e:
        raise SchemaError(f"Invalid payload schema for action {action}: {e}") from e
    
    return Message(
        type=msg_type,
        action=action,
        payload=payload,
        msg_id=obj.get("msg_id"),
        ok=obj.get("ok"),
        error=obj.get("error"),
    )