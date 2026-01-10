from session.session import Session
from protocol.message import Message
from protocol.enums import Action

from protocol.payloads.room import (
    CreateRoomPayload
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

def fetch_room_list(session: Session) -> Message:
    req = Message.request(Action.FETCH_ROOM_LIST, EmptyPayload())
    resp = session.request_response(req)
    return resp

def leave_room(session: Session) -> Message:
    req = Message.request(Action.LEAVE_ROOM, EmptyPayload())
    resp = session.request_response(req)
    return resp