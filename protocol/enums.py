from enum import Enum

class MessageType(Enum):
    REQUEST = 'request'
    RESPONSE = 'response'
    EVENT = 'event'

class Action(Enum):
    LOGIN = 'auth.login'
    REGISTER = 'auth.register'
    LOGOUT = 'auth.logout'

class Role(Enum):
    PLAYER = 'player'
    DEVELOPER = 'developer'