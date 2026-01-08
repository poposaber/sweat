import customtkinter
from typing import Callable, Optional

class RoomPlayerRow(customtkinter.CTkFrame):
    def __init__(self, master, player_name: str, is_host: bool = False):
        super().__init__(master)

        self.player_label = customtkinter.CTkLabel(self, text=player_name, font=("Arial", 16))
        self.player_label.pack(side="left", padx=10, pady=5)

        if is_host:
            self.host_label = customtkinter.CTkLabel(self, text="(Host)", font=("Arial", 12), text_color="red")
            self.host_label.pack(side="left", padx=10, pady=5)