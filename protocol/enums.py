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
    DOWNLOAD_GAME_INIT = 'game.download_init'
    DOWNLOAD_GAME_CHUNK = 'game.download_chunk'
    DOWNLOAD_GAME_FINISH = 'game.download_finish'
    FETCH_MY_WORKS = 'game.fetch_my_works'
    FETCH_STORE = 'game.fetch_store'
    FETCH_GAME_COVER = 'game.fetch_cover'
    FETCH_GAME_DETAIL = 'game.fetch_detail'

class Role(Enum):
    PLAYER = 'player'
    DEVELOPER = 'developer'