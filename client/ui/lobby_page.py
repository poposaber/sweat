import customtkinter as ctk
from typing import Callable, Optional

class LobbyPage(ctk.CTkFrame):
    def __init__(self, master, logout_callback: Optional[Callable[[], None]] = None):
        super().__init__(master, width=800, height=550)

        ctk.CTkLabel(self, text="Lobby").pack(pady=10)
        ctk.CTkButton(
            self, text="Logout",
            command=logout_callback
        ).pack()
