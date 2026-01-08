import customtkinter
from typing import Callable, Optional
from ..components.my_game_row_container import MyGameRowContainer
from client.infra.library_manager import LibraryManager
from tkinter import messagebox


class MyGamePage(customtkinter.CTkFrame):
    def __init__(self, master, 
                 library_manager: Optional[LibraryManager] = None, 
                 fetch_game_detail_callback: Optional[Callable[[str, Callable[[str, str, int, int, str], None], Callable[[Exception], None]], None]] = None,
                 download_callback: Optional[Callable[[str, Callable[[], None], Callable[[Exception], None], Callable[[int, int], None]], None]] = None, 
                 create_room_callback: Optional[Callable[[str, Callable[[str], None], Callable[[Exception], None]], None]] = None):
        super().__init__(master)
        self.game_row_container = MyGameRowContainer(self, width=600, height=400)
        self.game_row_container.place(relx=0.5, rely=0.5, relheight=1, relwidth=1, anchor=customtkinter.CENTER)
        self._library_manager = library_manager
        self._download_callback = download_callback
        self._create_room_callback = create_room_callback
        self._fetch_game_detail_callback = fetch_game_detail_callback

    def set_library_manager(self, library_manager: Optional[LibraryManager]):
        self._library_manager = library_manager

    def _on_create_room_click(self, game_name: str):
        if self._create_room_callback:
            self._create_room_callback(
                game_name,
                self._on_create_room_success,
                self._on_error
            )

    def refresh_games(self):
        # 1. Get games from local manifest
        if not self._library_manager:
            self.game_row_container.clear_game_rows()
            return
        self._library_manager.ensure_library_exists()
        installed_games = self._library_manager.get_installed_games()
        
        # 2. Clear existing rows (you might need to add a clear method to container)
        self.game_row_container.clear_game_rows()
        
        # 3. Add rows
        for game_name, game_info in installed_games.items():
            version = game_info["version"]
            min_players = game_info["min_players"]
            max_players = game_info["max_players"]
            self.game_row_container.add_game_row(
                game_name, version, min_players, max_players, lambda: None
            )
        if self._fetch_game_detail_callback:
            for game_name, game_info in installed_games.items():
                version = game_info["version"]
                self._fetch_game_detail_callback(
                    game_name,
                    lambda dv, gv, minp, maxp, gd, localver=version, game_name=game_name: self.on_fetch_game_detail(game_name, gv, localver),
                    self._on_error
                )

    def on_fetch_game_detail(self, game_name: str, game_version: str, local_version: str):
        # print(f"Fetched details for {game_name}: version {game_version}, local version {local_version}")
        if not self._download_callback:
            return
        # print(f"Comparing versions for {game_name}: fetched {game_version} vs local {local_version}")
        if game_version != local_version:
            self.game_row_container.set_game_row_button(
                game_name,
                "Update",
                lambda game_name=game_name: self._download_callback(
                    game_name,
                    self._on_download_complete,
                    self._on_error,
                    lambda downloaded, total: print(f"Downloading {game_name}: {downloaded}/{total} bytes")
                ) if self._download_callback else None
            )
        else:
            self.game_row_container.set_game_row_button(
                game_name,
                "Create Room",
                lambda game_name=game_name: self._on_create_room_click(game_name)
            )

    def _on_download_complete(self):
        messagebox.showinfo("Download Complete", "Updated successfully.")
        self.refresh_games()

    def _on_create_room_success(self, room_id: str):
        messagebox.showinfo("Room Created", f"Room created successfully! Room ID: {room_id}\nYou can go to 'My Room' tab to manage it.")

    def _on_error(self, error: Exception):
        messagebox.showerror("Error", str(error))

