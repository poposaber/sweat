import customtkinter
from typing import Callable, Optional
from ..components.tabbar import TabBar
from ..slides.rooms_slide import RoomsSlide
from ..slides.players_slide import PlayersSlide

class ThisLobbyPage(customtkinter.CTkFrame):
    def __init__(self, master, 
                 fetch_room_list_callback: Optional[Callable[[Callable[[list[tuple[str, str, str, int, int, str]]], None], Callable[[Exception], None]], None]] = None, 
                 fetch_player_list_callback: Optional[Callable[[Callable[[list[str]], None], Callable[[Exception], None]], None]] = None,
                 on_join_room_click: Optional[Callable[[str, str], None]] = None):
        super().__init__(master)
        self.tab_bar = TabBar(self, self.on_tabbar_select)
        self.tab_bar.place_default()
        self.rooms_slide = RoomsSlide(self, fetch_room_list_callback=fetch_room_list_callback, on_join_room_click=on_join_room_click)
        self.players_slide = PlayersSlide(self, fetch_player_list_callback=fetch_player_list_callback)
        self.tab_bar.add_tab("rooms", "Rooms", self.rooms_slide)
        self.tab_bar.add_tab("players", "Players", self.players_slide)
        self.tab_bar.show("rooms")

    def reset(self):
        self.tab_bar.show("rooms")
        self.after(100, self.rooms_slide.refresh_rooms)

    def on_tabbar_select(self, tab_id: str):
        print(f"Selected tab: {tab_id}")
        if tab_id == "rooms":
            # Delay refresh slightly to avoid race condition where widgets 
            # are destroyed while trying to redraw due to tab switch
            self.after(100, self.rooms_slide.refresh_rooms)
        elif tab_id == "players":
            self.players_slide.refresh_players()
    
    def add_room(self, room_id: str, host: str, game_name: str, players: int, max_players: int, status: str):
        self.rooms_slide.add_room(room_id, host, game_name, players, max_players, status)

    def remove_room(self, room_id: str):
        self.rooms_slide.remove_room(room_id)

    def update_room(self, room_id: str, host: str, game_name: str, players: int, max_players: int, status: str):
        self.rooms_slide.update_room(room_id, host, game_name, players, max_players, status)