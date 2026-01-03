import customtkinter
from typing import Callable, Optional
from ..components.game_block_container import GameBlockContainer
from tkinter import messagebox

class StorePage(customtkinter.CTkFrame):
    def __init__(self, master, 
                 fetch_store_callback: Optional[Callable[[int, int, Callable[[list[tuple[str, str, int, int]], int], None], Callable[[Exception], None]], None]] = None,
                 fetch_cover_callback: Optional[Callable[[str, Callable[[bytes], None], Callable[[Exception], None]], None]] = None):
        super().__init__(master)
        self.fetch_store_callback = fetch_store_callback
        self.fetch_cover_callback = fetch_cover_callback
        self.page = 1
        self.page_size = 20
        self.total_count = 0

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.game_block_container = GameBlockContainer(self)
        self.game_block_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.controls_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # self.prev_button = customtkinter.CTkButton(self.controls_frame, text="Previous", command=self.prev_page, state="disabled")
        # self.prev_button.pack(side="left", padx=10)
        
        # self.page_label = customtkinter.CTkLabel(self.controls_frame, text=f"Page {self.page}")
        # self.page_label.pack(side="left", padx=10)
        
        self.load_more_button = customtkinter.CTkButton(self.controls_frame, text="Load More", command=self.next_page, state="disabled")
        self.load_more_button.pack(side="bottom", pady=10)

    def load_games(self):
        if self.fetch_store_callback:
            self.fetch_store_callback(self.page, self.page_size, self.on_games_loaded, self.on_error)

    def on_games_loaded(self, games: list[tuple[str, str, int, int]], total_count: int):
        self.total_count = total_count
        
        game_data: list[tuple[str, str, int, int, Optional[bytes], Optional[Callable[[], None]]]] = [
            (game_name, version, min_players, max_players, None, lambda game_name=game_name: print(f"Clicked on {game_name}")) 
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

    def on_cover_loaded(self, game_name: str, cover_data: bytes):
        if not cover_data:
            return
        block = self.game_block_container.get_block(game_name)
        if block:
            block.update_cover(cover_data)

    def on_error(self, error: Exception):
        messagebox.showerror("Error", f"Failed to load games: {error}")

    def update_controls(self):
        if self.page * self.page_size < self.total_count:
            self.load_more_button.configure(state="normal", text="Load More")
        else:
            self.load_more_button.configure(state="disabled", text="No More Games")

    def next_page(self):
        self.page += 1
        self.load_games()

    def reset(self):
        self.page = 1
        self.load_games()