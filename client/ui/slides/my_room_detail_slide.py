import customtkinter
from typing import Callable, Optional
from ..components.room_player_row_container import RoomPlayerRowContainer
from tkinter import messagebox

class MyRoomDetailSlide(customtkinter.CTkFrame):
    def __init__(self, master, 
                 on_leave_callback: Optional[Callable[[], None]] = None, 
                 start_game_callback: Optional[Callable[[str, Callable[[], None], Callable[[Exception], None]], None]] = None):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self._room_id: str = ""
        self._game_name: str = ""
        self._max_players: int = 0

        self.info_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_columnconfigure(1, weight=1)
        self.info_frame.grid_columnconfigure(2, weight=0)
        self.info_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.room_id_label = customtkinter.CTkLabel(self.info_frame, text="Room ID: N/A", font=("Arial", 16))
        self.room_id_label.grid(row=0, column=0, padx=(10, 5), pady=(10, 5), sticky="w")
        self.game_name_label = customtkinter.CTkLabel(self.info_frame, text="Game: N/A", font=("Arial", 16))
        self.game_name_label.grid(row=0, column=1, padx=(5, 10), pady=(10, 5), sticky="w")
        self.max_players_label = customtkinter.CTkLabel(self.info_frame, text="Max Players: N/A", font=("Arial", 16))
        self.max_players_label.grid(row=0, column=2, padx=(5, 10), pady=(10, 5), sticky="e")

        self.room_players_container = RoomPlayerRowContainer(self)
        self.room_players_container.grid(row=1, column=0, columnspan=2, padx=(10, 5), pady=(5, 10), sticky="nsew")
        self.leave_button = customtkinter.CTkButton(
            self, text="Leave Room",
            command=lambda: on_leave_callback() if on_leave_callback else None
        )
        self.leave_button.grid(row=2, column=0, padx=(10, 5), pady=(5, 10), sticky="w")
        self._start_game_callback = start_game_callback
        self.start_game_button = customtkinter.CTkButton(
            self, text="Start Game",
            command=self.on_start_game_click
        )
        self.start_game_button.grid(row=2, column=1, padx=(5, 10), pady=(5, 10), sticky="e")

    def get_room_id(self) -> str:
        return self._room_id
    
    def set_room_id(self, room_id: str):
        self._room_id = room_id
        self.room_id_label.configure(text=f"Room ID: {room_id}")

    def get_game_name(self) -> str:
        return self._game_name
    
    def set_game_name(self, game_name: str):
        self._game_name = game_name
        self.game_name_label.configure(text=f"Game: {game_name}")

    def get_max_players(self) -> int:
        return self._max_players
    
    def set_max_players(self, max_players: int):
        self._max_players = max_players
        self.max_players_label.configure(text=f"Max Players: {max_players}")

    def add_player(self, player_name: str, is_host: bool = False, is_you: bool = False):
        self.room_players_container.add_player_row(player_name, is_host, is_you)

    def clear_players(self):
        self.room_players_container.clear_player_rows()
        
    def on_start_game_click(self):
        self.start_game_button.configure(state="disabled", text="Starting...")
        if self._start_game_callback:
            self._start_game_callback(
                self._room_id,
                self._on_start_game_success,
                self._on_error
            )

    def _on_start_game_success(self):
        pass

    def _on_error(self, error: Exception):
        messagebox.showerror("Error", str(error))
        self.start_game_button.configure(state="normal", text="Start Game")

    def set_host_mode(self, is_host: bool):
        if is_host:
            self.start_game_button.configure(state="normal")
        else:
            self.start_game_button.configure(state="disabled")

    def reset(self):
        self._room_id = ""
        self._game_name = ""
        self._max_players = 0
        self.room_id_label.configure(text="Room ID: N/A")
        self.game_name_label.configure(text="Game: N/A")
        self.max_players_label.configure(text="Max Players: N/A")
        self.clear_players()
        self.start_game_button.configure(state="disabled", text="Start Game")
