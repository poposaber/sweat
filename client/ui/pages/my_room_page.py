import customtkinter
from typing import Callable, Optional
from ..slides.my_room_detail_slide import MyRoomDetailSlide
from tkinter import messagebox


class MyRoomPage(customtkinter.CTkFrame):
    def __init__(self, master, 
                 check_my_room_callback: Optional[Callable[[Callable[[bool, str, str, str, list[str], int, str], None], Callable[[Exception], None]], None]] = None, 
                 leave_room_callback: Optional[Callable[[Callable[[], None], Callable[[Exception], None]], None]] = None, 
                 start_game_callback: Optional[Callable[[str, Callable[[], None], Callable[[Exception], None]], None]] = None):
        super().__init__(master)
        self._check_my_room_callback = check_my_room_callback
        self._leave_room_callback = leave_room_callback
        self._start_game_callback = start_game_callback
        self.not_in_room_label = customtkinter.CTkLabel(self, text="You are not in a room!", font=("Arial", 20))
        self.not_in_room_label.place(relx=0.5, rely=0.3, anchor=customtkinter.CENTER)
        self.my_room_detail_slide = MyRoomDetailSlide(self, on_leave_callback=self.on_leave_room_click, start_game_callback=self._start_game_callback)

    def update_room_status(self):
        if self._check_my_room_callback:
            self._check_my_room_callback(
                self._on_check_my_room_success,
                self._on_error
            )
    
    def switch_to_room(self, room_id: str, game_name: str, max_players: int):
        self.not_in_room_label.place_forget()
        self.my_room_detail_slide.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor=customtkinter.CENTER)
        self.my_room_detail_slide.set_game_name(game_name)
        self.my_room_detail_slide.set_room_id(room_id)
        self.my_room_detail_slide.set_max_players(max_players)

    def switch_to_no_room(self):
        self.my_room_detail_slide.place_forget()
        self.not_in_room_label.place(relx=0.5, rely=0.3, anchor=customtkinter.CENTER)
        self.my_room_detail_slide.reset()

    def _on_check_my_room_success(self, in_room: bool, room_id: str, game_name: str, host: str, players: list[str], max_players: int, username: str):
        if in_room:
            self.switch_to_room(room_id, game_name, max_players)
            self.set_room_players(players, host, username)
        else:
            self.switch_to_no_room()

    def set_room_players(self, players: list[str], host: str, username: str):
        self.my_room_detail_slide.clear_players()
        for player_name in players:
            self.my_room_detail_slide.add_player(player_name, is_host=(player_name == host), is_you=(player_name == username))
        self.my_room_detail_slide.set_host_mode(host == username)
    
    def _on_leave_room_success(self):
        self.switch_to_no_room()

    def _on_error(self, error: Exception):
        messagebox.showerror("Error", str(error))

    def on_leave_room_click(self):
        if self._leave_room_callback:
            self._leave_room_callback(
                self._on_leave_room_success,
                self._on_error
            )