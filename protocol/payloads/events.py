from dataclasses import dataclass

@dataclass
class RoomCreatedEventPayload:
    room_id: str
    host_username: str
    game_name: str
    current_players: int
    max_players: int
    status: str

@dataclass
class RoomRemovedEventPayload:
    room_id: str

@dataclass
class RoomUpdatedEventPayload:
    room_id: str
    host_username: str
    game_name: str
    current_players: int
    max_players: int
    status: str

@dataclass
class MyRoomUpdatedEventPayload:
    host_username: str
    game_name: str
    player_list: list[str]
    max_players: int
    status: str

@dataclass
class GameCheckEventPayload:
    game_name: str

@dataclass
class GameStartResultEventPayload:
    game_name: str
    port: int