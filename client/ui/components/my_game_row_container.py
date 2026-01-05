import customtkinter
from typing import Callable, Optional
from .row_container import RowContainer
from .my_game_row import MyGameRow

class MyGameRowContainer(RowContainer):
    def __init__(self, master, width: int = 400, height: int = 300):
        super().__init__(master, width=width, height=height)
        self._row_dict: dict[str, MyGameRow] = {}

    def add_game_row(self, game_name: str, version: str, min_players: int, max_players: int, button_callback: Optional[Callable[[], None]] = None):
        row = super().add_row(MyGameRow, game_name, version, min_players, max_players, button_callback)
        self._row_dict[game_name] = row

    def add_game_rows(self, games: list[tuple[str, str, int, int, Optional[Callable[[], None]]]]):
        for game in games:
            self.add_game_row(*game)
    
    def get_game_row(self, game_name: str) -> Optional[MyGameRow]:
        return self._row_dict.get(game_name)
    
    def clear_game_rows(self):
        super().clear_rows()
        self._row_dict.clear()

    def set_game_row_button(self, game_name: str, button_text: str, button_callback: Optional[Callable[[], None]] = None):
        row = self.get_game_row(game_name)
        if row:
            row.set_button(button_text, button_callback)

    def set_game_rows(self, games: list[tuple[str, str, int, int, Optional[Callable[[], None]]]]):
        self.clear_game_rows()
        self.add_game_rows(games)
    