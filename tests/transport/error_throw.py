from transport.errors import FramedSocketError
try:
    k = 1/0
except Exception as e:
    raise FramedSocketError("An error occurred", cause=e, peer=None, errno=None) from e