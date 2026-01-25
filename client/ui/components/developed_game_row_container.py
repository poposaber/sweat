import customtkinter
from typing import Callable, Optional
from .developed_game_row import DevelopedGameRow
from .row_container import RowContainer

class DevelopedGameRowContainer(RowContainer):
    def __init__(self, master, width: int = 400, height: int = 300):
        super().__init__(master, width=width, height=height)
        self._row_dict: dict[str, DevelopedGameRow] = {}

    def add_game_row(self, game_name: str, version: str, min_players: int, max_players: int, 
                     remove_command: Optional[Callable[[], None]] = None):
        row = super().add_row(DevelopedGameRow, game_name, version, min_players, max_players, remove_command)
        self._row_dict[game_name] = row

    def add_game_rows(self, games: list[tuple[str, str, int, int, Optional[Callable[[], None]]]]):
        for game in games:
            self.add_game_row(*game)
    
    def get_game_row(self, game_name: str) -> Optional[DevelopedGameRow]:
        return self._row_dict.get(game_name)
    
    def clear_game_rows(self):
        super().clear_rows()
        self._row_dict.clear()

    def set_game_rows(self, games: list[tuple[str, str, int, int, Optional[Callable[[], None]]]]):
        self.clear_game_rows()
        self.add_game_rows(games)
    