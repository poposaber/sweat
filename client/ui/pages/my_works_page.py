import customtkinter
from typing import Callable, Optional
import tkinter
from ..components.row_container import RowContainer
from ..components.developed_game_row import DevelopedGameRow

class MyWorksPage(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # self.label = customtkinter.CTkLabel(self, text="My Works Page", font=("Arial", 20))
        # self.label.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)
        self._row_container = RowContainer(self)
        self._row_container.place(relx=0.5, rely=0.5, relwidth=1, relheight=0.8, anchor=tkinter.CENTER)
        
        self._empty_label = customtkinter.CTkLabel(self, text="No games found", font=("Arial", 16))
        self._empty_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    def add_game_row(self, game_name: str, version: str, min_players: int, max_players: int, command: Optional[Callable[[], None]] = None):
        self._empty_label.place_forget()
        # row = DevelopedGameRow(self._row_container, game_name, version, min_players, max_players, command)
        # self._row_container.add_row(row)
        self._row_container.add_row(DevelopedGameRow, game_name, version, min_players, max_players, command)

    def clear_games(self):
        self._row_container.clear_rows()
        self._empty_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
