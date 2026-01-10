import customtkinter
from tkinter import messagebox
from typing import Callable, Optional
from ..components.room_list_row_container import RoomListRowContainer

class RoomsSlide(customtkinter.CTkFrame):
    def __init__(self, master, 
                 fetch_room_list_callback: Optional[Callable[[Callable[[list[tuple[str, str, str, int, str]]], None], Callable[[Exception], None]], None]] = None):
        super().__init__(master, fg_color="transparent")
        self._fetch_room_list_callback = fetch_room_list_callback
        self.room_list_container = RoomListRowContainer(self)
        self.room_list_container.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor=customtkinter.CENTER)

    def refresh_rooms(self):
        if self._fetch_room_list_callback:
            self._fetch_room_list_callback(
                self._on_fetch_room_list_success,
                self._on_error
            )

    def _on_fetch_room_list_success(self, rooms: list[tuple[str, str, str, int, str]]):
        self.room_list_container.set_room_rows(rooms)

    def _on_error(self, error: Exception):
        messagebox.showerror("Error", str(error))
    
    def add_room(self, room_id: str, host: str, game_name: str, players: int, status: str):
        self.room_list_container.add_room_row(room_id, host, game_name, players, status)