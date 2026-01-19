from typing import Callable, Optional
from .row_container import RowContainer
from .player_list_row import PlayerListRow

class PlayerListRowContainer(RowContainer):
    def __init__(self, master, width: int = 400, height: int = 300):
        super().__init__(master, width=width, height=height)
        self._row_dict: dict[str, PlayerListRow] = {}

    def add_player_row(self, player_name: str):
        row = super().add_row(PlayerListRow, player_name)
        self._row_dict[player_name] = row

    def add_player_rows(self, players: list[str]):
        for player in players:
            self.add_player_row(player)

    def remove_player_row(self, player_name: str):
        row = self._row_dict.get(player_name)
        if row:
            super().remove_row(row)
            del self._row_dict[player_name]
    
    def get_player_row(self, player_name: str) -> Optional[PlayerListRow]:
        return self._row_dict.get(player_name)
    
    def clear_player_rows(self):
        super().clear_rows()
        self._row_dict.clear()

    def set_player_rows(self, players: list[str]):
        self.clear_player_rows()
        self.add_player_rows(players)