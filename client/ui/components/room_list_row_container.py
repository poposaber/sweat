import customtkinter
from typing import Callable, Optional
from .row_container import RowContainer
from .room_list_row import RoomListRow

class RoomListRowContainer(RowContainer):
    def __init__(self, master, width: int = 400, height: int = 300):
        super().__init__(master, width=width, height=height)
        self._row_dict: dict[str, RoomListRow] = {}

    def add_room_row(self, room_id: str, host: str, game_name: str, player_count: int, max_players: int, status: str, on_join_room_click: Optional[Callable[[], None]] = None):
        row = super().add_row(RoomListRow, room_id, host, game_name, player_count, max_players, status, on_join_room_click)
        self._row_dict[room_id] = row

    def add_room_rows(self, rooms: list[tuple[str, str, str, int, int, str, Optional[Callable[[], None]]]]):
        for room in rooms:
            self.add_room_row(*room)

    def remove_room_row(self, room_id: str):
        row = self._row_dict.get(room_id)
        if row:
            super().remove_row(row)
            del self._row_dict[room_id]
    
    def get_room_row(self, room_id: str) -> Optional[RoomListRow]:
        return self._row_dict.get(room_id)
    
    def update_room_row(self, room_id: str, host: str, game_name: str, player_count: int, max_players: int, status: str):
        row = self._row_dict.get(room_id)
        if row:
            row.update_row(host, game_name, player_count, max_players, status)
    
    def clear_room_rows(self):
        super().clear_rows()
        self._row_dict.clear()

    def set_room_rows(self, rooms: list[tuple[str, str, str, int, int, str, Optional[Callable[[], None]]]]):
        self.clear_room_rows()
        self.add_room_rows(rooms)

    def is_empty(self) -> bool:
        return len(self._row_dict) == 0
