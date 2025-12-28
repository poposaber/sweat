import customtkinter as ctk
from typing import Callable, Optional

class LobbyView(ctk.CTkFrame):
    def __init__(self, master, logout_callback: Optional[Callable[[], None]] = None):
        super().__init__(master)

        ctk.CTkLabel(self, text="Lobby").place(relx=0.5, rely=0.3, anchor=ctk.CENTER)
        ctk.CTkButton(
            self, text="Logout",
            command=logout_callback
        ).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.geom_size = "800x600"