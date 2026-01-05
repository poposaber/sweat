import customtkinter
from typing import Callable, Optional
from ..slides.game_list_slide import GameListSlide
from ..slides.game_detail_slide import GameDetailSlide

class StorePage(customtkinter.CTkFrame):
    def __init__(self, master, 
                 fetch_store_callback: Optional[Callable[[int, int, Callable[[list[tuple[str, str, int, int]], int], None], Callable[[Exception], None]], None]] = None,
                 fetch_cover_callback: Optional[Callable[[str, Callable[[bytes], None], Callable[[Exception], None]], None]] = None, 
                 fetch_game_detail_callback: Optional[Callable[[str, Callable[[str, str, int, int, str], None], Callable[[Exception], None]], None]] = None, 
                 download_callback: Optional[Callable[[str, Callable[[], None], Callable[[Exception], None], Callable[[int, int], None]], None]] = None):
        super().__init__(master)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.game_list_slide = GameListSlide(self, 
                                             fetch_store_callback=fetch_store_callback, 
                                             fetch_cover_callback=fetch_cover_callback,
                                             on_game_click_callback=self.show_game_details)
        self.game_detail_slide = GameDetailSlide(self, 
                                                 on_back_click_callback=self.show_game_list,
                                                 fetch_game_detail_callback=fetch_game_detail_callback,
                                                 fetch_cover_callback=fetch_cover_callback, 
                                                 download_callback=download_callback)

        self.show_game_list()

    def show_game_list(self):
        self.game_detail_slide.grid_forget()
        self.game_list_slide.grid(row=0, column=0, sticky="nsew")

    def show_game_details(self, game_name: str, version: str, min_players: int, max_players: int):
        self.game_list_slide.grid_forget()
        self.game_detail_slide.display_game(game_name, version, min_players, max_players)
        self.game_detail_slide.grid(row=0, column=0, sticky="nsew")

    def reset(self):
        self.show_game_list()
        self.game_list_slide.reset()
