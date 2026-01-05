import customtkinter
from typing import Callable, Optional
from tkinter import messagebox, Event
from ..components.game_block_container import GameBlockContainer

class GameListSlide(customtkinter.CTkFrame):
    def __init__(self, master, 
                 fetch_store_callback: Optional[Callable[[int, int, Callable[[list[tuple[str, str, int, int]], int], None], Callable[[Exception], None]], None]] = None,
                 fetch_cover_callback: Optional[Callable[[str, Callable[[bytes], None], Callable[[Exception], None]], None]] = None,
                 on_game_click_callback: Optional[Callable[[str, str, int, int], None]] = None):
        super().__init__(master, fg_color="transparent")
        
        self.fetch_store_callback = fetch_store_callback
        self.fetch_cover_callback = fetch_cover_callback
        self.on_game_click_callback = on_game_click_callback
        
        self.page = 1
        self.page_size = 20
        self.total_count = 0
        self.is_loading = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.game_block_container = GameBlockContainer(self)
        self.game_block_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.controls_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        self.bind_scroll_events()
        
        self.load_more_button = customtkinter.CTkButton(self.controls_frame, text="Load More", command=self.next_page, state="disabled")
        self.load_more_button.pack(side="bottom", pady=10)

    def bind_scroll_events(self):
        self.game_block_container.bind("<MouseWheel>", self.check_scroll_position, add="+")
        self.game_block_container.bind("<Button-4>", self.check_scroll_position, add="+")
        self.game_block_container.bind("<Button-5>", self.check_scroll_position, add="+")

    def check_scroll_position(self, event: Event):
        if self.is_loading:
            return
        
        if event.delta > 0:
            return  # Scrolling up, ignore

        try:
            # yview returns (top_fraction, bottom_fraction)
            # If bottom_fraction is near 1.0, we are at the bottom
            _, bottom = self.game_block_container._parent_canvas.yview()
            if bottom >= 0.95: 
                self.next_page()
        except Exception:
            pass

    def load_games(self):
        if self.is_loading:
            return
        
        self.is_loading = True
        self.load_more_button.configure(state="disabled", text="Loading...")

        if self.fetch_store_callback:
            self.fetch_store_callback(self.page, self.page_size, self.on_games_loaded, self.on_error)

    def on_games_loaded(self, games: list[tuple[str, str, int, int]], total_count: int):
        self.is_loading = False
        self.total_count = total_count
        
        game_data: list[tuple[str, str, int, int, Optional[bytes], Optional[Callable[[], None]]]] = [
            (game_name, version, min_players, max_players, None, 
             lambda gn=game_name, v=version, minp=min_players, maxp=max_players: self.on_game_click(gn, v, minp, maxp))
            for (game_name, version, min_players, max_players) in games
        ]

        if self.page == 1:
            self.game_block_container.set_blocks(game_data)
        else:
            self.game_block_container.add_blocks(game_data)
            
        self.update_controls()
        
        # Fetch covers for loaded games
        if self.fetch_cover_callback:
            for game_name, _, _, _ in games:
                self.fetch_cover_callback(game_name, lambda data, name=game_name: self.on_cover_loaded(name, data), lambda e: print(f"Cover fetch error: {e}"))

    def on_game_click(self, game_name, version, min_players, max_players):
        if self.on_game_click_callback:
            self.on_game_click_callback(game_name, version, min_players, max_players)

    def on_cover_loaded(self, game_name: str, cover_data: bytes):
        if not cover_data:
            return
        block = self.game_block_container.get_block(game_name)
        if block:
            block.update_cover(cover_data)

    def on_error(self, error: Exception):
        self.is_loading = False
        self.update_controls()
        messagebox.showerror("Error", f"Failed to load games: {error}")

    def update_controls(self):
        if self.page * self.page_size < self.total_count:
            self.load_more_button.configure(state="normal", text="Load More")
        else:
            self.load_more_button.configure(state="disabled", text="No More Games")

    def next_page(self):
        if self.page * self.page_size >= self.total_count:
            # print("All games loaded.")
            return
        self.page += 1
        self.load_games()

    def reset(self):
        self.page = 1
        self.load_games()