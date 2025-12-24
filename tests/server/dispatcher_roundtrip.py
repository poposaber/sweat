from server.dispatcher import Dispatcher
from protocol.enums import Action, MessageType
from protocol.message import Message
from protocol.payloads.auth import Credential
from protocol.payloads.common import EmptyPayload

# Minimal tests for dispatcher routing

d = Dispatcher()

# LOGIN
req_login = Message.request(Action.LOGIN, Credential(username="user", password="pass"))
resp_login = d.dispatch(req_login)
assert resp_login.type == MessageType.RESPONSE
assert resp_login.action == Action.LOGIN
assert isinstance(resp_login.payload, type(Credential("","")))
assert resp_login.payload.username == "user"
assert resp_login.msg_id == req_login.msg_id
assert resp_login.ok is True

# REGISTER
req_reg = Message.request(Action.REGISTER, Credential(username="new", password="pwd"))
resp_reg = d.dispatch(req_reg)
assert resp_reg.type == MessageType.RESPONSE
assert resp_reg.action == Action.REGISTER
assert isinstance(resp_reg.payload, type(Credential("","")))
assert resp_reg.payload.username == "new"
assert resp_reg.msg_id == req_reg.msg_id
assert resp_reg.ok is True

# LOGOUT
req_logout = Message.request(Action.LOGOUT, EmptyPayload())
resp_logout = d.dispatch(req_logout)
assert resp_logout.type == MessageType.RESPONSE
assert resp_logout.action == Action.LOGOUT
assert isinstance(resp_logout.payload, type(EmptyPayload()))
assert resp_logout.msg_id == req_logout.msg_id
assert resp_logout.ok is True

print("server dispatcher tests passed")
