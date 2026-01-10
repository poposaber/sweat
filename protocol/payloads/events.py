from dataclasses import dataclass
from protocol.enums import RoomStatus

@dataclass
class RoomCreatedEventPayload:
    room_id: str
    host_username: str
    game_name: str
    current_players: int
    status: str
