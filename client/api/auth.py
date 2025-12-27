from session.session import Session
from protocol.message import Message
from protocol.enums import Action
from protocol.payloads.auth import Credential
from protocol.payloads.common import EmptyPayload


def login(session: Session, username: str, password: str, role: str) -> Message:
	req = Message.request(Action.LOGIN, Credential(username=username, password=password, role=role))
	return session.request_response(req)

def register(session: Session, username: str, password: str, role: str) -> Message:
    req = Message.request(Action.REGISTER, Credential(username=username, password=password, role=role))
    return session.request_response(req)

def logout(session: Session) -> Message:
	req = Message.request(Action.LOGOUT, EmptyPayload())
	return session.request_response(req)
