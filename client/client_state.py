from enum import Enum

class ClientState(Enum):
    DISCONNECTED = 0
    LOGGED_OUT = 1
    IN_LOBBY = 2