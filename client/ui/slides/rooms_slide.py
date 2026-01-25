import customtkinter
from tkinter import messagebox
from typing import Callable, Optional
from ..components.room_list_row_container import RoomListRowContainer

class RoomsSlide(customtkinter.CTkFrame):
    def __init__(self, master, 
                 fetch_room_list_callback: Optional[Callable[[Callable[[list[tuple[str, str, str, int, int, str]]], None], Callable[[Exception], None]], None]] = None, 
                 on_join_room_click: Optional[Callable[[str, str], None]] = None):
        super().__init__(master, fg_color="transparent")
        self._fetch_room_list_callback = fetch_room_list_callback
        self._on_join_room_click = on_join_room_click
        self.room_list_container = RoomListRowContainer(self)
        self.room_list_container.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor=customtkinter.CENTER)
        self.no_rooms_label = customtkinter.CTkLabel(self, text="No rooms available.", font=("Arial", 16))
        # self.no_rooms_label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

    def refresh_rooms(self):
        if self._fetch_room_list_callback:
            self._fetch_room_list_callback(
                self._on_fetch_room_list_success,
                self._on_error
            )

    def _on_fetch_room_list_success(self, rooms: list[tuple[str, str, str, int, int, str]]):
        if not rooms:
            self.no_rooms_label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
            self.room_list_container.clear_room_rows()
            self.room_list_container.place_forget()
            return
        else:
            self.no_rooms_label.place_forget()
            self.room_list_container.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor=customtkinter.CENTER)

        def button_callback(room_id: str, game_name: str):
            if self._on_join_room_click:
                self._on_join_room_click(room_id, game_name)
        
        # Explicit type hint to satisfy the list variance check
        room_with_callbacks: list[tuple[str, str, str, int, int, str, Optional[Callable[[], None]]]] = [
            (room_id, host, game_name, players, max_players, status, lambda rid=room_id, gname=game_name: button_callback(rid, gname))
            for room_id, host, game_name, players, max_players, status in rooms
        ]
        self.room_list_container.set_room_rows(room_with_callbacks)
        

    def _on_error(self, error: Exception):
        messagebox.showerror("Error", str(error))
    
    def add_room(self, room_id: str, host: str, game_name: str, players: int, max_players: int, status: str):
        if self.room_list_container.is_empty():
            self.no_rooms_label.place_forget()
            self.room_list_container.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor=customtkinter.CENTER)
        self.room_list_container.add_room_row(room_id, host, game_name, players, max_players, status)
    
    def remove_room(self, room_id: str):
        self.room_list_container.remove_room_row(room_id)
        if self.room_list_container.is_empty():
            self.no_rooms_label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
            self.room_list_container.place_forget()

    def update_room(self, room_id: str, host: str, game_name: str, players: int, max_players: int, status: str):
        self.room_list_container.update_room_row(room_id, host, game_name, players, max_players, status)