import customtkinter
from typing import Callable, Optional
from .clickable_row import ClickableRow

class DevelopedGameRow(ClickableRow):
    def __init__(self, master, game_name: str, version: str, min_players: int, max_players: int, command: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, height=40, command=command, **kwargs)

        self.game_name_label = customtkinter.CTkLabel(self, text=game_name, font=("Arial", 14), fg_color="transparent")
        self.game_name_label.place(relx=0.1, rely=0.5, anchor="w")

        self.min_max_label = customtkinter.CTkLabel(self, text=f"Players: {min_players}~{max_players}", font=("Arial", 12), fg_color="transparent")
        self.min_max_label.place(relx=0.5, rely=0.5, anchor="center")

        self.version_label = customtkinter.CTkLabel(self, text=f"Version: {version}", font=("Arial", 12), fg_color="transparent")
        self.version_label.place(relx=0.9, rely=0.5, anchor="e")