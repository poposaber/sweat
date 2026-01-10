import customtkinter as ctk
from typing import Callable, Optional
from ..components.tabbar import TabBar
from ..pages.account_page import AccountPage
from ..pages.my_room_page import MyRoomPage
from ..pages.store_page import StorePage
from ..pages.my_game_page import MyGamePage
from ..pages.this_lobby_page import ThisLobbyPage
from client.infra.library_manager import LibraryManager
from tkinter import messagebox

class LobbyView(ctk.CTkFrame):
    def __init__(self, master, logout_callback: Optional[Callable[[], None]] = None, 
                 fetch_store_callback: Optional[Callable[[int, int, Callable[[list[tuple[str, str, int, int]], int], None], Callable[[Exception], None]], None]] = None,
                 fetch_cover_callback: Optional[Callable[[str, Callable[[bytes], None], Callable[[Exception], None]], None]] = None, 
                 fetch_game_detail_callback: Optional[Callable[[str, Callable[[str, str, int, int, str], None], Callable[[Exception], None]], None]] = None, 
                 download_callback: Optional[Callable[[str, Callable[[], None], Callable[[Exception], None], Callable[[int, int], None]], None]] = None, 
                 create_room_callback: Optional[Callable[[str, Callable[[str], None], Callable[[Exception], None]], None]] = None, 
                 leave_room_callback: Optional[Callable[[Callable[[], None], Callable[[Exception], None]], None]] = None,
                 check_my_room_callback: Optional[Callable[[Callable[[bool, str, str, str, list[str], int, str], None], Callable[[Exception], None]], None]] = None,
                 fetch_room_list_callback: Optional[Callable[[Callable[[list[tuple[str, str, str, int, int, str]]], None], Callable[[Exception], None]], None]] = None,
                 library_manager: Optional[LibraryManager] = None):
        super().__init__(master)
        self._create_room_callback = create_room_callback
        self.store_page = StorePage(self, fetch_store_callback=fetch_store_callback, fetch_cover_callback=fetch_cover_callback, 
                                    fetch_game_detail_callback=fetch_game_detail_callback, download_callback=download_callback)
        self.my_game_page = MyGamePage(self, library_manager=library_manager, fetch_game_detail_callback=fetch_game_detail_callback, 
                                       download_callback=download_callback, on_create_room_click=self._on_create_room_click)
        self.this_lobby_page = ThisLobbyPage(self, fetch_room_list_callback=fetch_room_list_callback)
        self.my_room_page = MyRoomPage(self, check_my_room_callback=check_my_room_callback, leave_room_callback=leave_room_callback)
        self.account_page = AccountPage(self, logout_callback=logout_callback)
        self.tab_bar = TabBar(self, command=self._on_tabbar_click)
        self.tab_bar.add_tab("store", "Store", self.store_page, default=True)
        self.tab_bar.add_tab("my_games", "My Games", self.my_game_page)
        self.tab_bar.add_tab("this_lobby", "This Lobby", self.this_lobby_page)
        self.tab_bar.add_tab("my_room", "My Room", self.my_room_page)
        self.tab_bar.add_tab("account", "Account", self.account_page)
        self.tab_bar.place_default()

        self.geom_size = "800x600"

    def set_library_manager(self, library_manager: Optional[LibraryManager]):
        self.my_game_page.set_library_manager(library_manager)

    def _on_tabbar_click(self, tab_id: str):
        print(f"Tab clicked: {tab_id}")
        if tab_id == "store":
            self.store_page.reset()
        elif tab_id == "my_games":
            self.my_game_page.refresh_games()
        elif tab_id == "my_room":
            self.my_room_page.update_room_status()
        elif tab_id == "this_lobby":
            self.this_lobby_page.reset()

    def _on_create_room_click(self, game_name: str):
        if self._create_room_callback:
            self._create_room_callback(
                game_name,
                self._on_create_room_success,
                self._on_error
            )

    def _on_create_room_success(self, room_id: str):
        messagebox.showinfo("Room Created", f"Room created successfully! Room ID: {room_id}")
        self.tab_bar.show("my_room")
        self.my_room_page.update_room_status()

    def _on_error(self, error: Exception):
        messagebox.showerror("Error", str(error))

    # def set_store(self, games: list[tuple[str, str, int, int]]):
    #     self.store_page.game_block_container.set_blocks([
    #         (game_name, version, min_players, max_players, None, lambda game_name=game_name: print(f"Clicked on {game_name}")) for (game_name, version, min_players, max_players) in games
    #     ])

    def reset(self):
        self.tab_bar.show("store")