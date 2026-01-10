import customtkinter
from typing import Callable, Optional
from protocol.enums import RoomStatus

class RoomListRow(customtkinter.CTkFrame):
    def __init__(self, master, room_id: str, host: str, game_name: str, player_count: int, status: str):
        super().__init__(master)

        self.room_id = room_id
        self.host = host
        self.game_name = game_name
        self.player_count = player_count

        self.room_id_label = customtkinter.CTkLabel(self, text=f"Room ID: {room_id}", font=("Arial", 14))
        self.room_id_label.pack(side="left", padx=10, pady=5)

        self.host_label = customtkinter.CTkLabel(self, text=f"Host: {host}", font=("Arial", 14))
        self.host_label.pack(side="left", padx=10, pady=5)

        self.game_name_label = customtkinter.CTkLabel(self, text=f"Game: {game_name}", font=("Arial", 14))
        self.game_name_label.pack(side="left", padx=10, pady=5)

        self.player_count_label = customtkinter.CTkLabel(self, text=f"Players: {player_count}", font=("Arial", 14))
        self.player_count_label.pack(side="left", padx=10, pady=5)
        try:
            room_status = RoomStatus(status)
            status_text = room_status.name.replace("_", " ").title()
        except ValueError:
            status_text = "Unknown"

        self.status_label = customtkinter.CTkLabel(self, text=f"Status: {status_text}", font=("Arial", 14))
        self.status_label.pack(side="left", padx=10, pady=5)