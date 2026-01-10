import customtkinter
from typing import Callable, Optional
from ..components.tabbar import TabBar
from ..slides.rooms_slide import RoomsSlide
from ..slides.players_slide import PlayersSlide

class ThisLobbyPage(customtkinter.CTkFrame):
    def __init__(self, master, 
                 fetch_room_list_callback: Optional[Callable[[Callable[[list[tuple[str, str, str, int, str]]], None], Callable[[Exception], None]], None]] = None):
        super().__init__(master)
        self.tab_bar = TabBar(self, self.on_tabbar_select)
        self.tab_bar.place_default()
        self.rooms_slide = RoomsSlide(self, fetch_room_list_callback=fetch_room_list_callback)
        self.players_slide = PlayersSlide(self)
        self.tab_bar.add_tab("rooms", "Rooms", self.rooms_slide)
        self.tab_bar.add_tab("players", "Players", self.players_slide)
        self.tab_bar.show("rooms")

    def reset(self):
        self.tab_bar.show("rooms")
        self.rooms_slide.refresh_rooms()

    def on_tabbar_select(self, tab_id: str):
        print(f"Selected tab: {tab_id}")
        if tab_id == "rooms":
            self.rooms_slide.refresh_rooms()
    
    def add_room(self, room_id: str, host: str, game_name: str, players: int, status: str):
        self.rooms_slide.add_room(room_id, host, game_name, players, status)