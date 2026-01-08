from session.session import Session
from protocol.message import Message
from protocol.enums import Action

from protocol.payloads.room import (
    CreateRoomPayload, CreateRoomResponsePayload,
    LeaveRoomPayload
)

from protocol.payloads.common import EmptyPayload

def create_room(session: Session, game_name: str) -> Message:
    payload = CreateRoomPayload(game_name=game_name)
    req = Message.request(Action.CREATE_ROOM, payload)
    resp = session.request_response(req)
    return resp

def check_my_room(session: Session) -> Message:
    req = Message.request(Action.CHECK_MY_ROOM, EmptyPayload())
    resp = session.request_response(req)
    return resp