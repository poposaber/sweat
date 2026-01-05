import customtkinter
from typing import Callable, Optional
from io import BytesIO
from PIL import Image
from tkinter import messagebox

class GameDetailSlide(customtkinter.CTkFrame):
    def __init__(self, master, 
                 on_back_click_callback: Optional[Callable[[], None]] = None,
                 fetch_game_detail_callback: Optional[Callable[[str, Callable[[str, str, int, int, str], None], Callable[[Exception], None]], None]] = None,
                 fetch_cover_callback: Optional[Callable[[str, Callable[[bytes], None], Callable[[Exception], None]], None]] = None, 
                 download_callback: Optional[Callable[[str, Callable[[], None], Callable[[Exception], None], Callable[[int, int], None]], None]] = None):
        super().__init__(master, fg_color="transparent")
        self.on_back_click_callback = on_back_click_callback
        self.fetch_game_detail_callback = fetch_game_detail_callback
        self.fetch_cover_callback = fetch_cover_callback
        self.download_callback = download_callback
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top Bar
        self.top_bar = customtkinter.CTkFrame(self, fg_color="transparent", height=40)
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.back_button = customtkinter.CTkButton(self.top_bar, text="< Back", width=60, command=self.on_back_click)
        self.back_button.pack(side="left")

        # Content Area
        self.content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.content_frame.grid_columnconfigure(1, weight=1)

        # Cover Image
        self.cover_label = customtkinter.CTkLabel(self.content_frame, text="", width=256, height=256)
        self.cover_label.grid(row=0, column=1, rowspan=4, sticky="n", padx=(0, 20))

        # Game Info
        self.title_label = customtkinter.CTkLabel(self.content_frame, text="Game Title", font=("Arial", 24, "bold"), anchor="w")
        self.title_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        self.developer_label = customtkinter.CTkLabel(self.content_frame, text="Developer: Unknown", font=("Arial", 14), anchor="w")
        self.developer_label.grid(row=1, column=0, sticky="ew")

        self.version_label = customtkinter.CTkLabel(self.content_frame, text="Version: 1.0.0", font=("Arial", 14), anchor="w")
        self.version_label.grid(row=2, column=0, sticky="ew")

        self.players_label = customtkinter.CTkLabel(self.content_frame, text="Players: 1-4", font=("Arial", 14), anchor="w")
        self.players_label.grid(row=3, column=0, sticky="ew")

        self.description_textbox = customtkinter.CTkTextbox(self.content_frame, height=150)
        self.description_textbox.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=10)
        self.description_textbox.configure(state="disabled")

        self.download_button = customtkinter.CTkButton(self.content_frame, text="Download", height=40, font=("Arial", 16, "bold"))
        self.download_button.grid(row=5, column=0, columnspan=2, sticky="ew", pady=20)
    def on_back_click(self):
        if self.on_back_click_callback:
            self.on_back_click_callback()

    def display_game(self, game_name: str, version: str, min_players: int, max_players: int):
        self.title_label.configure(text=game_name)
        self.version_label.configure(text=f"Version: {version}")
        self.players_label.configure(text=f"Players: {min_players}-{max_players}")
        self.description_textbox.configure(state="normal")
        self.description_textbox.delete("1.0", "end")
        self.description_textbox.insert("1.0", "Loading description...")
        self.description_textbox.configure(state="disabled")
        self.download_button.configure(command=lambda: self.download_callback(
            game_name, 
            self.on_download_success, 
            self.on_download_error, 
            self.on_download_progress
        ) if self.download_callback else None)
        
        # Reset cover
        self.cover_label.configure(image=None)

        # Fetch details
        if self.fetch_game_detail_callback:
            self.fetch_game_detail_callback(game_name, self.on_detail_loaded, lambda e: print(f"Detail error: {e}"))

        # Fetch cover
        if self.fetch_cover_callback:
            self.fetch_cover_callback(game_name, self.on_cover_loaded, lambda e: print(f"Cover error: {e}"))

    def on_detail_loaded(self, developer, version, min_players, max_players, description):
        self.developer_label.configure(text=f"Developer: {developer}")
        self.description_textbox.configure(state="normal")
        self.description_textbox.delete("1.0", "end")
        self.description_textbox.insert("1.0", description)
        self.description_textbox.configure(state="disabled")

    def on_cover_loaded(self, cover_data: bytes):
        if not cover_data:
            return
        try:
            image_data = BytesIO(cover_data)
            pil_image = Image.open(image_data).resize((256, 256))
            ctk_image = customtkinter.CTkImage(pil_image, size=(256, 256))
            self.cover_label.configure(image=ctk_image)
        except Exception as e:
            print(f"Error loading cover image: {e}")

    def on_download_success(self):
        messagebox.showinfo("Download", "Game downloaded successfully!")

    def on_download_error(self, error_msg: Exception):
        messagebox.showerror("Download Error", f"Failed to download game: {str(error_msg)}")

    def on_download_progress(self, current: int, total: int):
        print(f"Download progress: {current}/{total}")
