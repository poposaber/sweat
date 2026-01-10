from dataclasses import dataclass

@dataclass
class CreateRoomPayload:
    game_name: str

@dataclass
class CreateRoomResponsePayload:
    room_id: str

@dataclass
class LeaveRoomPayload:
    room_id: str

@dataclass
class CheckMyRoomResponsePayload:
    in_room: bool
    room_id: str
    game_name: str
    host: str
    players: list[str]

@dataclass
class FetchRoomListResponsePayload:
    rooms: list[tuple[str, str, str, int, str]]  # (room_id, host, game_name, player_count, status)