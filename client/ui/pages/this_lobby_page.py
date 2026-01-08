import customtkinter
from typing import Callable, Optional
from ..components.tabbar import TabBar
from ..slides.rooms_slide import RoomsSlide
from ..slides.players_slide import PlayersSlide

class ThisLobbyPage(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.tab_bar = TabBar(self, self.on_tabbar_select)
        self.tab_bar.place_default()
        self.rooms_slide = RoomsSlide(self)
        self.players_slide = PlayersSlide(self)
        self.tab_bar.add_tab("rooms", "Rooms", self.rooms_slide)
        self.tab_bar.add_tab("players", "Players", self.players_slide)
        self.tab_bar.show("rooms")


    def on_tabbar_select(self, tab_id: str):
        print(f"Selected tab: {tab_id}")