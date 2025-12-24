from session.errors import SessionError
try:
    k = 1/0
except Exception as e:
    raise SessionError("An error occurred") from e