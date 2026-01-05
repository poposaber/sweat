import customtkinter
from typing import Callable, Optional
from io import BytesIO
from PIL import Image

NORMAL_FG_COLOR = "#3D3D3D"
HOVER_FG_COLOR = "#3A5779"
PRESSED_FG_COLOR = "#2A3C50"

class GameBlock(customtkinter.CTkFrame):
    def __init__(self, master, game_name: str, version: str, min_players: int, max_players: int, game_cover_bytes: Optional[bytes] = None, command: Optional[Callable[[], None]] = None):
        super().__init__(master, fg_color=NORMAL_FG_COLOR)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        if game_cover_bytes:
            image_data = BytesIO(game_cover_bytes)
        else:
            with open("client/ui/assets/default_game_cover.png", "rb") as f:
                default_image_data = f.read()
            image_data = BytesIO(default_image_data)

        self._game_name = game_name
        self._version = version
        self._min_players = min_players
        self._max_players = max_players
        self._game_cover_bytes = game_cover_bytes

        self._pil_image = Image.open(image_data).resize((128, 128))
        self.game_cover_image = customtkinter.CTkImage(self._pil_image, size=(128, 128))
        self.game_cover_image_label = customtkinter.CTkLabel(self, image=self.game_cover_image, text="", fg_color="transparent")
        self.game_cover_image_label.grid(row=0, column=0, sticky=customtkinter.W, padx=10, pady=10)

        self.game_label = customtkinter.CTkLabel(self, text=f"{game_name} (v{version})", font=("Arial", 16), fg_color="transparent", wraplength=128)
        self.game_label.grid(row=1, column=0, sticky=customtkinter.W, padx=10, pady=(10, 0))

        self.players_label = customtkinter.CTkLabel(self, text=f"Players: {min_players}-{max_players}", font=("Arial", 12), fg_color="transparent", wraplength=128)
        self.players_label.grid(row=2, column=0, sticky=customtkinter.W, padx=10, pady=(0, 10))

        widgets = [self, self.game_cover_image_label, self.game_label, self.players_label]

        if command:
            for widget in widgets:
                widget.bind("<Enter>", lambda e: self.configure(fg_color=HOVER_FG_COLOR))
                widget.bind("<Leave>", lambda e: self.configure(fg_color=NORMAL_FG_COLOR))
                widget.bind("<ButtonPress-1>", lambda e: self.configure(fg_color=PRESSED_FG_COLOR))
                widget.bind("<ButtonRelease-1>", lambda e: self.configure(fg_color=HOVER_FG_COLOR))
                widget.bind("<Button-1>", lambda e: command())

    def update_cover(self, cover_data: bytes):
        image_data = BytesIO(cover_data)
        self._pil_image = Image.open(image_data).resize((128, 128))
        self.game_cover_image = customtkinter.CTkImage(self._pil_image, size=(128, 128))
        self.game_cover_image_label.configure(image=self.game_cover_image)

    def get_image(self) -> Image.Image:
        return self._pil_image.copy()
    
    def get_game_name(self) -> str:
        return self._game_name
    
    def get_version(self) -> str:
        return self._version
    
    def get_player_range(self) -> tuple[int, int]:
        return (self._min_players, self._max_players)
    
    def get_cover_bytes(self) -> Optional[bytes]:
        return self._game_cover_bytes
        