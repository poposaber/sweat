from session.session import Session
from protocol.message import Message
from protocol.enums import Action

from protocol.payloads.game_launch import GameCheckResultPayload

from protocol.payloads.common import EmptyPayload

def start_game(session: Session) -> Message:
    req = Message.request(Action.START_GAME, EmptyPayload())
    resp = session.request_response(req)
    return resp

def send_game_check_result(session: Session, game_name: str, version: str, sha256: str) -> Message:
    payload = GameCheckResultPayload(game_name=game_name, version=version, sha256=sha256)
    req = Message.request(Action.GAME_CHECK_RESULT, payload)
    resp = session.request_response(req)
    return resp