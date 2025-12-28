from server.dispatcher import Dispatcher
from protocol.enums import Action, MessageType, Role
from protocol.message import Message
from protocol.payloads.auth import Credential
from protocol.payloads.common import EmptyPayload
from unittest.mock import MagicMock

# Minimal tests for dispatcher routing

# Mock dependencies
mock_db = MagicMock()
mock_db.get_player.return_value = ("user", "pass")
mock_db.create_player.return_value = True

mock_session_map = MagicMock()
mock_session_map.get_session_by_user.return_value = None
mock_session_map.get_user_by_session.return_value = (Role.PLAYER, "user")

mock_session = MagicMock()

d = Dispatcher(mock_db, mock_session_map)

# LOGIN
req_login = Message.request(Action.LOGIN, Credential(username="user", password="pass", role=Role.PLAYER.value))
resp_login = d.dispatch(req_login, mock_session)
assert resp_login.type == MessageType.RESPONSE
assert resp_login.action == Action.LOGIN
assert isinstance(resp_login.payload, Credential)
assert resp_login.payload.username == "user"
assert resp_login.msg_id == req_login.msg_id
assert resp_login.ok is True

# REGISTER
req_reg = Message.request(Action.REGISTER, Credential(username="new", password="pwd", role=Role.PLAYER.value))
resp_reg = d.dispatch(req_reg, mock_session)
assert resp_reg.type == MessageType.RESPONSE
assert resp_reg.action == Action.REGISTER
assert isinstance(resp_reg.payload, Credential)
assert resp_reg.payload.username == "new"
assert resp_reg.msg_id == req_reg.msg_id
assert resp_reg.ok is True

# LOGOUT
req_logout = Message.request(Action.LOGOUT, EmptyPayload())
resp_logout = d.dispatch(req_logout, mock_session)
assert resp_logout.type == MessageType.RESPONSE
assert resp_logout.action == Action.LOGOUT
assert isinstance(resp_logout.payload, type(EmptyPayload()))
assert resp_logout.msg_id == req_logout.msg_id
assert resp_logout.ok is True

print("server dispatcher tests passed")
