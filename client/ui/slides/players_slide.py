import customtkinter
from typing import Callable, Optional
from ..components.player_list_row_container import PlayerListRowContainer
from tkinter import messagebox

class PlayersSlide(customtkinter.CTkFrame):
    def __init__(self, master, fetch_player_list_callback: Optional[Callable[[Callable[[list[str]], None], Callable[[Exception], None]], None]] = None):
        super().__init__(master, fg_color="transparent")
        self._fetch_player_list_callback = fetch_player_list_callback
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.player_list_container = PlayerListRowContainer(self, width=300, height=400)
        self.player_list_container.grid(row=0, column=0, sticky=customtkinter.NSEW)

    def set_players(self, players: list[str]):
        self.player_list_container.set_player_rows(players)

    def add_player(self, player_name: str):
        self.player_list_container.add_player_row(player_name)

    def remove_player(self, player_name: str):
        self.player_list_container.remove_player_row(player_name)

    def on_fetch_player_list_success(self, players: list[str]):
        self.set_players(players)

    def on_error(self, error: Exception):
        messagebox.showerror("Error", str(error))

    def refresh_players(self):
        if self._fetch_player_list_callback:
            self._fetch_player_list_callback(
                self.on_fetch_player_list_success,
                self.on_error
            )

        