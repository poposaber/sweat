import customtkinter
from typing import Callable, Optional
from .row_container import RowContainer
from .room_player_row import RoomPlayerRow

class RoomPlayerRowContainer(RowContainer):
    def __init__(self, master, width: int = 400, height: int = 300):
        super().__init__(master, width=width, height=height)
        self._row_dict: dict[str, RoomPlayerRow] = {}

    def add_player_row(self, player_name: str, is_host: bool = False, is_you: bool = False):
        row = super().add_row(RoomPlayerRow, player_name, is_host, is_you)
        self._row_dict[player_name] = row

    def add_player_rows(self, players: list[tuple[str, bool, bool]]):
        for player in players:
            self.add_player_row(*player)

    def remove_player_row(self, player_name: str):
        row = self._row_dict.get(player_name)
        if row:
            super().remove_row(row)
            del self._row_dict[player_name]

    def get_player_row(self, player_name: str) -> Optional[RoomPlayerRow]:
        return self._row_dict.get(player_name)
    
    def clear_player_rows(self):
        super().clear_rows()
        self._row_dict.clear()

    def set_player_rows(self, players: list[tuple[str, bool, bool]]):
        self.clear_player_rows()
        self.add_player_rows(players)
        