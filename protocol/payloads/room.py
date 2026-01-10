from dataclasses import dataclass

@dataclass
class CreateRoomPayload:
    game_name: str

@dataclass
class CreateRoomResponsePayload:
    room_id: str

@dataclass
class CheckMyRoomResponsePayload:
    in_room: bool
    room_id: str
    game_name: str
    host: str
    players: list[str]
    max_players: int

@dataclass
class FetchRoomListResponsePayload:
    rooms: list[tuple[str, str, str, int, int, str]]  # (room_id, host, game_name, player_count, max_players, status)