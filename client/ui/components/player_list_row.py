import customtkinter
from typing import Callable, Optional

class PlayerListRow(customtkinter.CTkFrame):
    def __init__(self, master, player_name: str):
        super().__init__(master)
        self.player_name = player_name
        self.name_label = customtkinter.CTkLabel(self, text=player_name, font=("Arial", 14))
        self.name_label.pack(side="left", padx=10, pady=5)