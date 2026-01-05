import customtkinter
from typing import Callable, Optional

class MyGameRow(customtkinter.CTkFrame):
    def __init__(self, master, game_name: str, version: str, min_players: int, max_players: int, button_callback: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, height=40, **kwargs)

        self.game_name_label = customtkinter.CTkLabel(self, text=game_name, font=("Arial", 14), fg_color="transparent")
        self.game_name_label.place(relx=0.01, rely=0.5, anchor=customtkinter.W)

        self.version_label = customtkinter.CTkLabel(self, text=f"Version: {version}", font=("Arial", 12), fg_color="transparent")
        self.version_label.place(relx=0.4, rely=0.5, anchor=customtkinter.CENTER)

        self.player_range_label = customtkinter.CTkLabel(self, text=f"Players: {min_players}-{max_players}", font=("Arial", 12), fg_color="transparent")
        self.player_range_label.place(relx=0.6, rely=0.5, anchor=customtkinter.CENTER)

        self.interact_button = customtkinter.CTkButton(self, text="Create Room", width=80, height=30, command=button_callback)
        self.interact_button.place(relx=0.99, rely=0.5, anchor=customtkinter.E)

    def set_button(self, text: str, command: Optional[Callable[[], None]] = None):
        self.interact_button.configure(text=text, command=command)