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
    CREATE_ROOM = 'room.create'
    LEAVE_ROOM = 'room.leave'
    CHECK_MY_ROOM = 'room.check_my_room'
    FETCH_ROOM_LIST = 'room.fetch_list'
    # used in events
    ROOM_CREATED = 'room.created'
    ROOM_REMOVED = 'room.removed'
    ROOM_UPDATED = 'room.updated'
    MY_ROOM_UPDATED = 'room.my_room_updated'
    ROOM_PLAYER_JOINED = 'room.player_joined'
    ROOM_PLAYER_LEFT = 'room.player_left'

class RoomStatus(Enum):
    WAITING = 'waiting'
    STARTING = 'starting'
    IN_GAME = 'in_game'

class Role(Enum):
    PLAYER = 'player'
    DEVELOPER = 'developer'