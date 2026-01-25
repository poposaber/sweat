import customtkinter
from typing import Callable, Optional

class DevelopedGameRow(customtkinter.CTkFrame):
    def __init__(self, master, game_name: str, version: str, min_players: int, max_players: int, remove_command: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, height=40, **kwargs)

        self.game_name_label = customtkinter.CTkLabel(self, text=game_name, font=("Arial", 14), fg_color="transparent")
        self.game_name_label.place(relx=0.01, rely=0.5, anchor="w")

        self.min_max_label = customtkinter.CTkLabel(self, text=f"Players: {min_players}~{max_players}", font=("Arial", 12), fg_color="transparent")
        self.min_max_label.place(relx=0.4, rely=0.5, anchor="center")

        self.version_label = customtkinter.CTkLabel(self, text=f"Version: {version}", font=("Arial", 12), fg_color="transparent")
        self.version_label.place(relx=0.7, rely=0.5, anchor="e")

        self.remove_button = customtkinter.CTkButton(self, text="Remove", width=80, height=30, fg_color="#FF5C5C", hover_color="#FF3B3B", command=remove_command)
        self.remove_button.place(relx=0.99, rely=0.5, anchor="e")