from protocol.enums import Action, MessageType
from protocol.message import Message
from protocol.json_codec import encode, decode
from protocol.payloads.auth import Credential
from protocol.payloads.common import EmptyPayload

# Build a login request
req = Message.request(Action.LOGIN, Credential(username="user", password="pass"))
encoded = encode(req)
decoded = decode(encoded)

assert decoded.type == MessageType.REQUEST
assert decoded.action == Action.LOGIN
assert decoded.payload.username == "user"
assert decoded.payload.password == "pass"
assert decoded.msg_id == req.msg_id

# Build a logout response (EmptyPayload) correlated with request id
resp = Message.response(Action.LOGOUT, EmptyPayload(), msg_id=req.msg_id, ok=True)
encoded_resp = encode(resp)
decoded_resp = decode(encoded_resp)

assert decoded_resp.type == MessageType.RESPONSE
assert decoded_resp.action == Action.LOGOUT
assert isinstance(decoded_resp.payload, type(EmptyPayload()))
assert decoded_resp.msg_id == req.msg_id
assert decoded_resp.ok == True

print("protocol roundtrip_auth tests passed")
