from enum import Enum

class MessageType(Enum):
    REQUEST = 'request'
    RESPONSE = 'response'
    EVENT = 'event'

class Action(Enum):
    LOGIN = 'auth.login'
    REGISTER = 'auth.register'
    LOGOUT = 'auth.logout'
    UPLOAD_GAME_INIT = 'game.upload_init'
    UPLOAD_GAME_CHUNK = 'game.upload_chunk'
    UPLOAD_GAME_FINISH = 'game.upload_finish'
    UPLOAD_GAME_INIT_RESPONSE = 'game.upload_init_response'
    DOWNLOAD_GAME = 'game.download'

class Role(Enum):
    PLAYER = 'player'
    DEVELOPER = 'developer'